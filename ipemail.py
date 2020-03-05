import yaml
import netifaces
import smtplib


def get_ips():
    msg = ''
    for i in netifaces.interfaces():
        try:
            msg += f'{i}: {netifaces.ifaddresses(i)[netifaces.AF_INET][0]["addr"]}\n'
        except KeyError:
            msg += i + ': ERROR\n'
    return msg


def send_email(conf_loc, msg):
    with open(conf_loc, 'r') as stream:
        em_cf = yaml.safe_load(stream)
    body = (f"""From:{em_cf['from']}
Subject: {em_cf['sub']} \n
To: {em_cf['to']} \n""") + msg
    server = smtplib.SMTP_SSL(em_cf['host'], em_cf['port'])
    server.ehlo()
    server.login(em_cf['from'], em_cf['password'])
    server.sendmail(em_cf['from'], em_cf['to'], body)
    server.quit()


if __name__ == '__main__':
    send_email('configs/email_config.yml', get_ips())
