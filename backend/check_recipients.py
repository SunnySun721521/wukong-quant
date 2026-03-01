from email_config_manager import EmailConfigManager

config = EmailConfigManager().get_config()
print(f'收件人: {config.get("recipients", [])}')