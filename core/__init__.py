from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from decouple import config

import zope.sqlalchemy, logging.config

from .database.security import SecurityPolicy
from celery_app import celery

def get_session_factory(engine):
    """Return a generator of database session objects."""
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory

def get_tm_session(session_factory, transaction_manager):
    """Build a session and register it as a transaction-managed session."""
    dbsession = session_factory()
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    configuration = Configurator(settings=settings)
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    configuration.set_authorization_policy(ACLAuthorizationPolicy())
    configuration.include('pyramid_jwt')
    configuration.set_jwt_authentication_policy(settings['core.secret'], auth_type='Bearer', algorithm=settings['core.algorithm'])
    configuration.include('pyramid_jinja2')
    configuration.include('pyramid_bootstrap')
    configuration.include('pyramid_sqlalchemy')
    configuration.include('pyramid_tm')
    configuration.include('.routes')

    configuration.set_default_csrf_options(require_csrf=False)

    configuration.set_security_policy(SecurityPolicy(secret=settings['core.secret']))

    session_factory = get_session_factory(engine_from_config(settings, prefix='sqlalchemy.'))
    configuration.registry['dbsession_factory'] = session_factory
    
    configuration.add_request_method(
        lambda request: get_tm_session(session_factory, request.tm),
        'dbsession',
        reify=True
    )

    # Set Celery instance in the Pyramid registry
    configuration.registry.celery = celery

    # Configure logging using a file-based configuration
    logging.config.fileConfig(global_config['__file__'], disable_existing_loggers=False)

    configuration.scan()

    app = configuration.make_wsgi_app()
    return app