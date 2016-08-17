from negowl import docker, factory

if __name__ == '__main__':
    client = factory.get('scmesos06')
    client.update_image_2('meerkat', 'meerkat:0.0.1.build16')