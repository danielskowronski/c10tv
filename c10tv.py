#!/usr/bin/python3

import yaml,json,urllib,random,sys,denonavr,os,logging,websocket
from pylgtv import WebOsClient
from wsgiref.simple_server import make_server
from wakeonlan import send_magic_packet
from tg import MinimalApplicationConfigurator,expose,TGController,session,request
from tg.configurator.components.session import SessionConfigurationComponent
from tg.configurator.components.statics import StaticsConfigurationComponent

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

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
			w = WebOsClient(app_cfg['lg']['ip'])
			w.register()

			if "lg_arr_" in cmd:
				w.request("com.webos.service.networkinput/getPointerInputSocket")
				ws = websocket.WebSocket()
				ws.connect(w.last_response['payload']['socketPath'])
				if cmd=="lg_arr_down":
					ws.send('type:button\nname:DOWN\n\n')
				elif cmd=="lg_arr_up":
					ws.send('type:button\nname:UP\n\n')
				elif cmd=="lg_arr_left":
					ws.send('type:button\nname:LEFT\n\n')
				elif cmd=="lg_arr_right":
					ws.send('type:button\nname:RIGHT\n\n')
				elif cmd=="lg_arr_ok":
					ws.send('type:button\nname:ENTER\n\n')
				elif cmd=="lg_arr_back":
					ws.send('type:button\nname:BACK\n\n')
			elif cmd=="lg_cmd_pause":
				w.pause()
			elif cmd=="lg_input_netflix":
				w.launch_app(app_cfg['lg']['netflix'])
			elif cmd=="lg_input_ps4":
				w.set_input(app_cfg['lg']['ps4'])
			elif cmd=="lg_power_on":
				send_magic_packet(app_cfg['lg']['mac'])
			elif cmd=="lg_power_off":
				w.power_off()
			else:
				return '{"response":"invalid_cmd"}'
			
			return '{"response":"ok"}'

		else:
			return '{"response":"invalid_cmd"}'
		


config = MinimalApplicationConfigurator()
config.register(StaticsConfigurationComponent)
config.update_blueprint({
	'root_controller': RootController(),
	'serve_static': True,
	'paths': {
		'static_files': 'static'
	}
})
config.register(SessionConfigurationComponent)
config.serve_static = True
#config.paths['static_files'] = 'static'
stream = open('config.yml', 'r')
app_cfg = yaml.load(stream)['c10tv']
print('Serving on port '+str(app_cfg['port'])+'...')
httpd = make_server('', app_cfg['port'], config.make_wsgi_app())
httpd.serve_forever()