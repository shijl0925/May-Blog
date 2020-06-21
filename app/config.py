import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = b'********'
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///:memory:'

    MAIL_SERVER = '********'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = '********'
    MAIL_PASSWORD = '********'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    AVATARS_IDENTICON_ROWS = 7
    AVATARS_IDENTICON_COLS = 7
    AVATARS_IDENTICON_BG = None
    AVATARS_SIZE_TUPLE = (30, 150, 300)
    AVATARS_SAVE_PATH = os.path.join(basedir, 'avatars')

    AVATARS_CROP_BASE_WIDTH = 350

    # Flask-Security setup
    SECURITY_EMAIL_SENDER = MAIL_DEFAULT_SENDER
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_RECOVERABLE = True
    SECURITY_URL_PREFIX = '/auth'

    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"
    SECURITY_TRACKABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_POST_LOGIN_VIEW = SECURITY_POST_LOGOUT_VIEW = SECURITY_POST_REGISTER_VIEW = 'posts.posts'

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    CKEDITOR_HEIGHT = 400
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_CODE_THEME = "monokai_sublime"

    UPLOADED_PATH = os.path.join(basedir, 'uploads')
    CKEDITOR_FILE_UPLOADER = "posts.upload"

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

    FILEUPLOAD_LOCALSTORAGE_IMG_FOLDER = "uploads"
    FILEUPLOAD_PREFIX = "/file"
    FILEUPLOAD_ALLOWED_EXTENSIONS = ['jpg', 'gif', 'png', 'jpeg']


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(DevelopmentConfig):
    pass


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'postgresql://deploy:deploy@deploy@localhost/analysis'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

security_messages = {
    'SECURITY_MSG_UNAUTHORIZED': (
        '您没有权限查看/操作该资源.', 'error'),
    'SECURITY_MSG_CONFIRM_REGISTRATION': (
        '谢谢.确认指示已被送往 %(email)s.', 'success'),
    'SECURITY_MSG_EMAIL_CONFIRMED': (
        '谢谢.您的邮箱已被证实.', 'success'),
    'SECURITY_MSG_ALREADY_CONFIRMED': (
        '您的电子邮件已确认.', 'info'),
    'SECURITY_MSG_INVALID_CONFIRMATION_TOKEN': (
        '无效的确认标记.', 'error'),
    'SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED': (
        '%(email)s 已经与帐户相关联.', 'error'),
    'SECURITY_MSG_PASSWORD_MISMATCH': (
        '密码不匹配', 'error'),
    'SECURITY_MSG_RETYPE_PASSWORD_MISMATCH': (
        '密码不匹配', 'error'),
    'SECURITY_MSG_INVALID_REDIRECT': (
        '外域重定向被禁止', 'error'),
    'SECURITY_MSG_PASSWORD_RESET_REQUEST': (
        '重置您的密码已发送到 %(email)s.', 'info'),
    'SECURITY_MSG_PASSWORD_RESET_EXPIRED': (
        '你没有在重置密码 %(within)s. 新的指令已被送往 '
        ' %(email)s.', 'error'),
    'SECURITY_MSG_INVALID_RESET_PASSWORD_TOKEN': (
        '无效的重置密码令牌.', 'error'),
    'SECURITY_MSG_CONFIRMATION_REQUIRED': (
        '电子邮件需要确认.', 'error'),
    'SECURITY_MSG_CONFIRMATION_REQUEST': (
        '确认指示已被送往 %(email)s.', 'info'),
    'SECURITY_MSG_CONFIRMATION_EXPIRED': (
        '你没有在确认您的电子邮件 %(within)s. 新的指令来确认您的电子邮件 '
        '已发送到 %(email)s.', 'error'),
    'SECURITY_MSG_LOGIN_EXPIRED': (
        '您没有权限登录 %(within)s. 新的登录指令已被送往 '
        '%(email)s.', 'error'),
    'SECURITY_MSG_LOGIN_EMAIL_SENT': (
        '已发送登录的指示 %(email)s.', 'success'),
    'SECURITY_MSG_INVALID_LOGIN_TOKEN': (
        '无效登录令牌.', 'error'),
    'SECURITY_MSG_DISABLED_ACCOUNT': (
        '帐户被禁用.', 'error'),
    'SECURITY_MSG_EMAIL_NOT_PROVIDED': (
        '未提供电子邮件', 'error'),
    'SECURITY_MSG_INVALID_EMAIL_ADDRESS': (
        '无效的电子邮件地址', 'error'),
    'SECURITY_MSG_PASSWORD_NOT_PROVIDED': (
        '未提供密码', 'error'),
    'SECURITY_MSG_PASSWORD_NOT_SET': (
        '无密码为该用户设置', 'error'),
    'SECURITY_MSG_PASSWORD_INVALID_LENGTH': (
        '密码必须至少6个字符', 'error'),
    'SECURITY_MSG_USER_DOES_NOT_EXIST': (
        '指定用户不存在', 'error'),
    'SECURITY_MSG_INVALID_PASSWORD': (
        '无效密码', 'error'),
    'SECURITY_MSG_PASSWORDLESS_LOGIN_SUCCESSFUL': (
        '您已经成功登录.', 'success'),
    'SECURITY_MSG_PASSWORD_RESET': (
        '您成功重置您的密码,您已自动登录.',
        'success'),
    'SECURITY_MSG_PASSWORD_IS_THE_SAME': (
        '您的新密码必须与以前的密码不同.', 'error'),
    'SECURITY_MSG_PASSWORD_CHANGE': (
        '您成功地改变了你的密码.', 'success'),
    'SECURITY_MSG_LOGIN': (
        '请登录访问此页.', 'info'),
    'SECURITY_MSG_REFRESH': (
        '请验证访问此页面.', 'info'),
    'SECURITY_MSG_FORGOT_PASSWORD': (
        '忘记密码？', 'info'),
    'SECURITY_MSG_LDAP_SERVER_DOWN': (
        'LDAP服务器连接失败', 'error'),
    'SECURITY_MSG_LDAP_EMAIL_NOT_PROVIDED': (
        '此LDAP账户不存在邮箱', 'error'),
}
