import configparser

cfg = configparser.ConfigParser()
cfg.read('motor_controller/config.ini')


def test_config_sections():
    sections = cfg.sections()
    assert 'motor' in sections
    assert 'gpio' in sections
    assert 'fan' in sections
