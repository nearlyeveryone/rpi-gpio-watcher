import time
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker


class ControlModel(object):
    pass


def loadSession():
    """"""
    dbPath = '/home/nearlyeveryone/WebApi.db'
    #dbPath = '/home/pi/publish/WebApi.db'
    engine = create_engine('sqlite:///%s' % dbPath, echo=True)

    metadata = MetaData(engine)
    control_models = Table('ControlModels', metadata, autoload=True)
    mapper(ControlModel, control_models)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def automaticDoor(controlModel):
    if controlModel.Value:
        controlModel.Status = 'Idiot'
        session.commit()


def moveCamera(controlModel):
    if controlModel.Value:
        controlModel.Status = 'Idiot'
        session.commit()


def feeder(controlModel):
    pass


if __name__ == "__main__":
    session = loadSession()
    while(true):
        controlModels = session.query(ControlModel).all()
        for i, controlModel in enumerate(controlModels):
            if controlModel.Description == 'Automatic Door':
                automaticDoor(controlModel)
            if controlModel.Description == 'Move Camera':
                moveCamera(controlModel)
            if controlModel.Description == 'Feeder':
                feeder(controlModel)
        time.sleep(3)
