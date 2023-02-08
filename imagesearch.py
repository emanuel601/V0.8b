import os
from google_images_search import GoogleImagesSearch
from db_definitions import db, CarBrand, CarModel, ImageDataBase, app


# you can provide API key and CX using arguments,
# or you can set environment variables: GCS_DEVELOPER_KEY, GCS_CX

gis = GoogleImagesSearch(os.getenv('API-KEY'), os.getenv('API-KEY-2'))


def image_search(q_image):

    searched_image = db.session.query(ImageDataBase).filter_by(q_image=q_image).first()
    try:
        print(searched_image.q_image)
        print('this works')
        return searched_image.url_image
    except AttributeError:
        # define search params
        # option for commonly used search param are shown below for easy reference.
        # For param marked with '##':
        #   - Multiselect is currently not feasible. Choose ONE option only
        #   - This param can also be omitted from _search_params if you do not wish to define any value
        _search_params = {
            'q': q_image,
            'num': 1,
            'rights': 'cc_publicdomain|cc_attribute|cc_sharealike',
            'imgType': 'photo'
        }

        gis.search(search_params=_search_params)
        with app.app_context():
            new_image = ImageDataBase(
                q_image=q_image,
                url_image=gis.results()[0].url
            )
            db.session.add(new_image)
            db.session.commit()

        return gis.results()[0].url

    # for image in gis.results():
    #     print(image.url)


def fulfill_carrousel():
    with app.app_context():
        popular_cars = db.session.query(CarModel).order_by(CarModel.cantidad.desc()).limit(5).all()

        images_to_search = [f'{db.session.query(CarBrand).filter_by(id=car.parent_id).first().marca} {car.modelo}'
                            for car in popular_cars]

    images_carrousel = [(image_search(query_image), query_image) for query_image in images_to_search]

    return images_carrousel


def fulfill_images_db():
    with app.app_context():
        popular_cars = db.session.query(CarModel).order_by(CarModel.cantidad.desc()).limit(200).all()

        images_to_search = [f'{db.session.query(CarBrand).filter_by(id=car.parent_id).first().marca} {car.modelo}'
                            for car in popular_cars]

        images_carrousel = [(image_search(query_image), query_image) for query_image in images_to_search]

    return images_carrousel

