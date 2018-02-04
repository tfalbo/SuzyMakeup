import os

try:
    os.remove('suzymakeup.db')
except OSError:
    pass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base,Category, Item


engine = create_engine('sqlite:///suzymakeup.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
    minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
    ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
    voluptate velit esse cillum dolore eu fugiat nulla pariatur.
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
    deserunt mollit anim id est laborum."""


# Lips

category1 = Category(name="Lips")
session.add(category1)
session.commit()

lips_item1 = Item(name="Cat Lipstick",
                description=lorem,
                price="19.99",
                photo_filename="lips1.jpg",
                category=category1)

session.add(lips_item1)
session.commit()


lips_item2 = Item(name="Cat Lipstick",
                description=lorem,
                price="24.99",
                photo_filename="lips2.jpg",
                category=category1)

session.add(lips_item2)
session.commit()

# Eyes

category2 = Category(name="Eyes")
session.add(category2)
session.commit

eyes_item1 = Item(name="Cat Eyeshadow",
                description=lorem,
                price="29.99",
                photo_filename="eyes1.jpg",
                category=category2)

session.add(eyes_item1)
session.commit()

eyes_item2 = Item(name="Cat Eyeshadow",
                description=lorem,
                price="29.99",
                photo_filename="eyes2.jpg",
                category=category2)

session.add(eyes_item2)
session.commit()

eyes_item3 = Item(name="Cat Eyeshadow Kit",
                description=lorem,
                price="39.99",
                photo_filename="eyes3.jpg",
                category=category2)

session.add(eyes_item3)
session.commit()

eyes_item4 = Item(name="Cat Mascara",
                description=lorem,
                price="29.99",
                photo_filename="eyes4.jpg",
                category=category2)

session.add(eyes_item4)
session.commit()

# Face
category3 = Category(name="Face")
session.add(category3)
session.commit()

face_item1 = Item(name="Cat Blush",
                description=lorem,
                price="15.99",
                photo_filename="face1.jpg",
                category=category3)

session.add(face_item1)
session.commit()

face_item1 = Item(name="Cat Blush",
                description=lorem,
                price="15.99",
                photo_filename="face2.jpg",
                category=category3)

session.add(face_item1)
session.commit()



# Accessories
category4 = Category(name="Accessories")
session.add(category4)
session.commit()

accessories_item1 = Item(name="Cat Band",
                description=lorem,
                price="15.99",
                photo_filename="access1.png",
                category=category4)

session.add(accessories_item1)
session.commit()

accessories_item2 = Item(name="Cat Pouch",
                description=lorem,
                price="10.99",
                photo_filename="access2.png",
                category=category4)

session.add(accessories_item2)
session.commit()

accessories_item3 = Item(name="Cat Pouch",
                description=lorem,
                price="10.99",
                photo_filename="access3.png",
                category=category4)

session.add(accessories_item3)
session.commit()

accessories_item4 = Item(name="Cat Pouch",
                description=lorem,
                price="10.99",
                photo_filename="access4.png",
                category=category4)

session.add(accessories_item4)
session.commit()



# Accessories
category5 = Category(name="Brushes")
session.add(category5)
session.commit()

brushes_item1 = Item(name="Cat Paw Brush",
                description=lorem,
                price="5.99",
                photo_filename="brush1.jpg",
                category=category5)

session.add(brushes_item1)
session.commit()


print ("added items!")
