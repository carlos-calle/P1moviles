def get_itu_profile(profile_name):
    """
    Retorna el diccionario con los parámetros del perfil de canal solicitado,
    de acuerdo a la recomendación ITU-R M.1225.
    Los retardos devueltos están intencionalmente multiplicados por mil (para ser ingresados 
    como microsegundos visualmente) sirviendo al diseño original estipulado.
    """
    profiles_data = {
        'ITU Pedestrian A': {
            'delays': "0, 0.000110, 0.000190, 0.000410",
            'gains': "0.0, -9.7, -19.2, -22.8",
            'v': "3"
        },
        'ITU Pedestrian B': {
            'delays': "0, 0.000200, 0.000800, 0.001200, 0.002300, 0.003700",
            'gains': "0.0, -0.9, -4.9, -8.0, -7.8, -23.9",
            'v': "3"
        },
        'ITU Vehicular A': {
            'delays': "0, 0.000310, 0.000710, 0.001090, 0.001730, 0.002510",
            'gains': "0.0, -1.0, -9.0, -10.0, -15.0, -20.0",
            'v': "60"
        },
        'ITU Vehicular B': {
            'delays': "0, 0.000300, 0.008900, 0.012900, 0.017100, 0.020000",
            'gains': "-2.5, 0.0, -12.8, -10.0, -25.2, -16.0",
            'v': "120"
        }
    }
    return profiles_data.get(profile_name, None)
