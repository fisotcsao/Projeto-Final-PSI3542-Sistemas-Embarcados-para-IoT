# Complete project details at https://RandomNerdTutorials.com/micropython-mqtt-publish-dht11-dht22-esp32-esp8266/

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin
import dht
esp.osdebug(None)
import gc
gc.collect()

#ssid = 'KOFUJI_2022'
#password = 'b0r@b0r@'
ssid = 'Galaxy S20 FE9D0B'
password = 'caiocaio'
mqtt_server = '192.168.1.XXX'
#EXAMPLE IP ADDRESS or DOMAIN NAME
mqtt_server = '3.124.62.105'

client_id = ubinascii.hexlify(machine.unique_id())

topic_sub = b'esp-led'
topic_pub_temp = b'esp-10884301/dht/temperature'
topic_pub_hum = b'esp-10884301/dht/humidity'

last_message = 0
message_interval = 5

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(True)
wlan_mac = wlan_sta.config('mac')

station_mac = station.config('mac')

while station.isconnected() == False:
  pass

print('Connection successful')

print(ubinascii.hexlify(station_mac).decode().upper())

# Definição das variáveis

#rele = Pin(2)
rele = Pin(2, Pin.OUT)
last_message = 0
message_interval = 1
sensor = dht.DHT22(Pin(15))

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  
# Aqui recebemos os comandos vindos do mqtt publisher ao qual estamos inscritos.
# Aqui o esp funciona como subscriber.
def sub_cb(topic, msg):
  print((topic, msg))
  if msg == b'liga':
    rele.value(1)
    print('Rele ligado')
  elif msg == b'desliga':
    rele.value(0)
    print('Rele desligado')


def read_sensor():
  try:
    sensor.measure()
    temp = sensor.temperature()
    # uncomment for Fahrenheit
    #temp = temp * (9/5) + 32.0
    hum = sensor.humidity()
    if (isinstance(temp, float) and isinstance(hum, float)) or (isinstance(temp, int) and isinstance(hum, int)):
      temp = (b'{0:3.1f},'.format(temp))
      hum =  (b'{0:3.1f},'.format(hum))
      return temp, hum
    else:
      return('Invalid sensor readings.')
  except OSError as e:
    return('Failed to read sensor.')

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
      temp, hum = read_sensor()
      print(temp)
      print(hum)
      client.publish(topic_pub_temp, temp)
      client.publish(topic_pub_hum, hum)
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()

# Aqui enviamos os comandos para o mqtt que está inscrito como subscriber.
# Aqui o esp funciona como publisher 
