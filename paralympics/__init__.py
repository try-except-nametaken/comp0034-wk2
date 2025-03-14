from flask import Flask
from markupsafe import escape
from flask import current_app as app
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app(test_config=None):
    # create the Flask app
    app = Flask(__name__, instance_relative_config=True)
    # configure the Flask app (see later notes on how to generate your own SECRET_KEY)
    app.config.from_mapping(
        SECRET_KEY='GtTfEda0EOCkL55-HLJqQw',
        # Set the location of the database file called paralympics.sqlite which will be in the app's instance folder
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, 'paralympics.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass



# Initialise Flask with the SQLAlchemy database extension
    db.init_app(app)
    # Models are defined in the models module, so you must import them before
    # will not know about them.
    from paralympics.model import User, Region, Event
    # Create the tables in the database
    # create_all does not update tables if they are already in the database
    with app.app_context():
        db.create_all()
        # Register the routes with the app in the context
        # add_data_from_csv()
        from paralympics import paralympics
    return app


import csv
from pathlib import Path


def add_data_from_csv():
    """Adds data to the database if it does not already exist."""

    # Add import here and not at the top of the file to avoid circular import issues
    from paralympics.model import Region, Event

    # If there are no regions in the database, then add them
    first_region = db.session.execute(db.select(Region)).first()
    if not first_region:
        print("Start adding region data to the database")
        noc_file = Path(__file__).parent.parent.joinpath("data", "noc_regions.csv")
        with open(noc_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                # row[0] is the first column, row[1] is the second column
                r = Region(NOC=row[0], region=row[1], notes=row[2])
                db.session.add(r)
            db.session.commit()

    # If there are no Events, then add them
    first_event = db.session.execute(db.select(Event)).first()
    if not first_event:
        print("Start adding event data to the database")
        event_file = Path(__file__).parent.parent.joinpath("data", "paralympic_events.csv")
        with open(event_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                # row[0] is the first column, row[1] is the second column etc
                # For int data types, if there is no value, set to None rather than ''
                e = Event(type=row[0],
                          year=row[1],
                          country=row[2],
                          host=row[3],
                          NOC=row[4],
                          start=row[5],
                          end=row[6],
                          duration=row[7] or None,
                          disabilities_included=row[8],
                          countries=row[9] or None,
                          events=row[10] or None,
                          sports=row[11] or None,
                          participants_m=row[12] or None,
                          participants_f=row[13] or None,
                          participants=row[14] or None,
                          highlights=row[15])
                db.session.add(e)
            db.session.commit()

