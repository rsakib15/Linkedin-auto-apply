import yaml
import pdb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from linkedineasyapply import LinkedinEasyApply
from validate_email import validate_email
from selenium.webdriver.chrome.service import Service

def init_browser():
    chrome_options = Options()
    # Uncomment this line if you need to run the browser headlessly
    # chrome_options.add_argument("--headless")

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.set_window_position(0, 0)
    driver.maximize_window()

    return driver

def validate_yaml():
    with open("config.yaml", 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    mandatory_params = ['email', 'password', 'disableAntiLock', 'remote', 'experienceLevel', 'jobTypes', 'date',
                        'positions', 'locations', 'distance', 'outputFileDirectory', 'checkboxes', 'universityGpa',
                        'languages', 'industry', 'technology', 'personalInfo', 'eeo', 'uploads']

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise Exception(mandatory_param + ' is not inside the yml file!')

    assert validate_email(parameters['email'])
    assert len(str(parameters['password'])) > 0

    assert isinstance(parameters['disableAntiLock'], bool)
    assert isinstance(parameters['remote'], bool)

    assert len(parameters['jobTypes']) > 0
    job_types = parameters.get('jobTypes', {})
    at_least_one_job_type = any(job_types.values())
    assert at_least_one_job_type

    assert len(parameters['date']) > 0
    date = parameters.get('date', {})
    at_least_one_date = any(date.values())
    assert at_least_one_date

    approved_distances = {0, 5, 10, 25, 50, 100}
    assert parameters['distance'] in approved_distances

    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0

    assert len(parameters['uploads']) >= 1 and 'resume' in parameters['uploads']

    assert len(parameters['checkboxes']) > 0
    checkboxes = parameters.get('checkboxes', {})
    assert isinstance(checkboxes.get('driversLicence'), bool)
    assert isinstance(checkboxes.get('requireVisa'), bool)
    assert isinstance(checkboxes.get('legallyAuthorized'), bool)
    assert isinstance(checkboxes.get('urgentFill'), bool)
    assert isinstance(checkboxes.get('commute'), bool)
    assert isinstance(checkboxes.get('backgroundCheck'), bool)
    assert 'degreeCompleted' in checkboxes

    assert isinstance(parameters['universityGpa'], (int, float))

    languages = parameters.get('languages', {})
    language_types = {'none', 'conversational', 'professional', 'native or bilingual'}
    for language in languages.values():
        assert language.lower() in language_types

    industry = parameters.get('industry', {})
    for skill in industry.values():
        assert isinstance(skill, int)
    assert 'default' in industry

    technology = parameters.get('technology', {})
    for tech in technology.values():
        assert isinstance(tech, int)
    assert 'default' in technology

    assert len(parameters['personalInfo']) > 0
    personal_info = parameters.get('personalInfo', {})
    for info in personal_info.values():
        assert info != ''

    assert len(parameters['eeo']) > 0
    eeo = parameters.get('eeo', {})
    for survey_question in eeo.values():
        assert survey_question != ''

    return parameters

if __name__ == '__main__':
    parameters = validate_yaml()
    browser = init_browser()
    bot = LinkedinEasyApply(parameters, browser)
    bot.login()
    bot.security_check()
    bot.start_applying()
