def get_itu_profile(profile_name):
    """
    Retorna el diccionario con los parámetros del perfil de canal solicitado,
    de acuerdo a la recomendación ITU-R M.1225.
    Los retardos se entregan en microsegundos para coincidir con la entrada de la GUI.
    """
    profiles_data = {
        'ITU Pedestrian A': {
            'delays': "0, 0.110, 0.190, 0.410",
            'gains': "0.0, -9.7, -19.2, -22.8",
            'v': "3"
        },
        'ITU Pedestrian B': {
            'delays': "0, 0.200, 0.800, 1.200, 2.300, 3.700",
            'gains': "0.0, -0.9, -4.9, -8.0, -7.8, -23.9",
            'v': "3"
        },
        'ITU Vehicular A': {
            'delays': "0, 0.310, 0.710, 1.090, 1.730, 2.510",
            'gains': "0.0, -1.0, -9.0, -10.0, -15.0, -20.0",
            'v': "60"
        },
        'ITU Vehicular B': {
            'delays': "0, 0.300, 8.900, 12.900, 17.100, 20.000",
            'gains': "-2.5, 0.0, -12.8, -10.0, -25.2, -16.0",
            'v': "120"
        }
    }
    return profiles_data.get(profile_name, None)
