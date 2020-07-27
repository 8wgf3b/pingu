import yaml
import netifaces
import smtplib
import zmq
from discord import Embed


def send_via_sock(msg):
    ctx = zmq.Context()
    for i in range(2):
        sock = ctx.socket(zmq.REQ)
        sock.setsockopt(zmq.RCVTIMEO, 500)
        sock.connect("tcp://localhost:5555")
        try:
            sock.send_pyobj(msg)
            break
        except (zmq.error.ZMQError, zmq.error.Again) as e:
            print(e)
            print(f'try {i + 1} failed')
            sock.close()
    try:
        print(sock.recv_pyobj())         
    except (zmq.error.ZMQError, zmq.error.Again) as e:
        print('receiving error')
    finally:
        sock.close()    
        
        
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
    msg = get_ips()
    try:
        send_email('configs/email_config.yml', msg)
    except Exception as e:
        pass
    embed = Embed(title='IP Addresses', description=msg)
    msg_dic = {'embed': embed}    
    send_via_sock(msg_dic)
            
    
    
