import undetected_chromedriver as uc


def create_driver(user_profile_dir):
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument("--user-data-dir={0}".format(user_profile_dir))
    options.page_load_strategy = 'eager'
    # TODO: patch patcher.py before using driver_executable_path
    driver = uc.Chrome(options=options, driver_executable_path='undetected_chromedriver.exe', use_subprocess=False)
    return driver
