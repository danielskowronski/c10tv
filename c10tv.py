#!/usr/bin/python3

import yaml,json,urllib,random,sys,denonavr,os
from wsgiref.simple_server import make_server
from tg import MinimalApplicationConfigurator,expose,TGController,session,request
from tg.configurator.components.session import SessionConfigurationComponent


class RootController(TGController):
	@expose(content_type='text/html')
	def index(self):
		file = open('./index.html','r') 
		return file.read()

	@expose(content_type='application/json')
	def cmd(self,cmd):
		if "denon" in cmd:
			d = denonavr.DenonAVR(app_cfg['denon']['ip'])
			d.update()

			if cmd=="denon_input_digital":
				d.input_func = app_cfg['denon']['digital_in']
			elif cmd=="denon_power_off":
				d.power_off()
			elif cmd=="denon_power_on":
				d.power_on()
			elif cmd=="denon_vol_down":
				d.volume_down()
			elif cmd=="denon_vol_mute":
				d.mute(True) #FIXME
			elif cmd=="denon_vol_up":
				d.volume_up()
			else:
				return '{"response":"invalid_cmd"}'

			return '{"response":"ok"}'


		elif "lg" in cmd:
			if cmd=="lg_cmd_down":
				cmd="DirectionDown"
			elif cmd=="lg_cmd_up":
				cmd="DirectionUp"
			elif cmd=="lg_cmd_left":
				cmd="DirectionLeft"
			elif cmd=="lg_cmd_right":
				cmd="DirectionRight"
			elif cmd=="lg_cmd_ok":
				cmd="Select"
			elif cmd=="lg_cmd_pause":
				cmd="Pause"
			elif cmd=="lg_input_netflix":
				cmd="netflix"
			elif cmd=="lg_input_ps4":
				cmd="InputHdmi3"
			elif cmd=="lg_power":
				cmd="PowerToggle"
			else:
				return '{"response":"invalid_cmd"}'
			
			oscmd=app_cfg['harmony']['path']+" --protocol WEBSOCKETS --harmony_ip "+app_cfg['harmony']['ip']+" send_command --device_id "+app_cfg['harmony']['lg_device']+" --command "+cmd
			print("EXEC: "+oscmd)
			os.system(oscmd)
			return '{"response":"ok"}'

		else:
			return '{"response":"invalid_cmd"}'
		


config = MinimalApplicationConfigurator()
config.update_blueprint({
	'root_controller': RootController()
})
config.register(SessionConfigurationComponent)
stream = open('config.yml', 'r')
app_cfg = yaml.load(stream)['c10tv']
print('Serving on port '+str(app_cfg['port'])+'...')
httpd = make_server('', app_cfg['port'], config.make_wsgi_app())
httpd.serve_forever()