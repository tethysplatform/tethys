from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import sessionmaker

from ckanapp.my_first_app.lib import get_persistent_store_engine

# DB Engine, sessionmaker and base
engine = get_persistent_store_engine('stream_gage_db')
SessionMaker = sessionmaker(bind=engine)
Base = declarative_base()

class StreamGage (Base):
    '''
    Example SQLAlchemy DB
    '''
    __tablename__ = 'stream_gages'

    # Columns
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    value = Column(Integer)

    def __init__(self, latitude, longitude, value):
        """
        Constructor for a gage
        """
        self.latitude = latitude
        self.longitude = longitude
        self.value = value

    @classmethod
    def get_gages_as_geojson(cls):
        '''
        Returns a GeoJSON object representing all gages in db
        '''
        # Create a session
        session = SessionMaker()

        # Query DB for gage objects
        gages = session.query(cls).all()

        # Create geojson object
        geojson_gages = {"type": "GeometryCollection",
                         "geometries": []}
        geometries = []

        # Create geometry objects for each gage
        for gage in gages:
            gage_geometry = dict(type="Point",
                                                     coordinates=[gage.latitude, gage.longitude],
                                 properties={"value": gage.value})
            geometries.append(gage_geometry)

        geojson_gages['geometries'] = geometries
        return geojson_gages
