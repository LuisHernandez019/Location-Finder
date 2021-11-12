import re
import folium
import flagpy as fp
from threading import Thread
from tkinter import Tk,PhotoImage,Frame,LabelFrame,Label,Entry,Radiobutton,StringVar,Button,messagebox
from geopy.geocoders import Nominatim
from html2image import Html2Image
from PIL import Image, ImageTk

def get_location_info(latitude,longitude):
   location = geolocator.reverse(f"{latitude},{longitude}", language='en')

   try:
      if ('city' in location.raw['address']):
         ccm = location.raw['address']['city']
      elif ('county' in location.raw['address']):
         ccm = location.raw['address']['county']
      elif ('municipality' in location.raw['address']):
         ccm = location.raw['address']['municipality']
      elif ('province' in location.raw['address']):
         ccm = location.raw['address']['province']
      else:
         ccm = 'No definido'

      if ('state' in location.raw['address']):
         state_region = location.raw['address']['state']
      else:
         state_region = ccm

      if ('country' in location.raw['address']):
         country = location.raw['address']['country']
         try:
            flag = fp.get_flag_img(country)
         except:
            country = 'The ' + country
            flag = fp.get_flag_img(country)
         finally:
            return [ccm,state_region,country,flag]
      else:
         country = ccm
         return [ccm,state_region,country]
   except:
      return False

def generate_map(latitude, longitude):
   folium_map = folium.Map(location=[latitude,longitude], zoom_start=15, zoom_control=False)
   folium.Marker([latitude,longitude], icon=folium.Icon(color="red")).add_to(folium_map)
   folium_map.save('map.html')
   hti.screenshot(html_file='map.html', save_as='map.png', size=(465, 425))

   img_map = ImageTk.PhotoImage(Image.open('map.png'))
   label_map.config(image=img_map)
   label_map.image = img_map

def update_info(latitude, longitude):
   location_data = get_location_info(latitude,longitude)
   Thread(target=generate_map,args=(latitude,longitude)).start()

   if location_data:
      label_city.config(text=location_data[0])
      label_state.config(text=location_data[1])
      label_country.config(text=location_data[2])

      if len(location_data) == 4:
         img_flag = ImageTk.PhotoImage(location_data[3])
         label_flag.config(image=img_flag)
         label_flag.image = img_flag
   else:
      label_city.config(text='No definido')
      label_state.config(text='No definido')
      label_country.config(text='No definido')
      img_flag = ImageTk.PhotoImage(Image.open('unknown_flag.png',).resize((175,90), Image.ANTIALIAS))
      label_flag.config(image=img_flag)
      label_flag.image = img_flag

def dms_to_dd(degree, minute, second, pos):
   int_d = int(degree)
   minute = minute/60
   second = second/3600

   if pos == 'N' or pos == 'E':
      pos = ''
   else:
      pos = '-'

   return (pos + str(int_d+(minute+second)))

def evaluate_location_DMS(degree_lat, minute_lat, second_lat, pos_lat, degree_lon, minute_lon, second_lon, pos_lon):
   try:
      m_lat = int(minute_lat)
      m_lon = int(minute_lon)
      s_lat = float(second_lat)
      s_lon = float(second_lon)

      if m_lat >= 0 and  m_lon >= 0 and s_lat >= 0 and s_lon >= 0 and m_lat <= 60 and m_lon <= 60 and s_lat <= 60 and s_lon <= 60:
         full_location = degree_lat + '°' + str(m_lat) + '\'' + str(s_lat) + '\"' + pos_lat + ' ' + degree_lon + '°' + str(m_lon) + '\'' + str(s_lon) + '\"' + pos_lon
         
         if re.match(pattern_location, full_location):
            latitude = dms_to_dd(degree_lat, m_lat, s_lat, pos_lat)
            longitude = dms_to_dd(degree_lon, m_lon, s_lon, pos_lon)
            update_info(latitude, longitude)
         else:
            messagebox.showerror(message="Los datos introducidos no son válidos.",title='Error al leer las coordenadas.')
      else:
         messagebox.showerror(message="Las minutos y segundos deben estar en un rango entre 0 y 60.",title='Rango inválido de coordenadas.')
   except:
      messagebox.showerror(message="No se han ingresado todas las coordenadas correctamente.",title='Error al leer las coordenadas.')

def evaluate_location_DD(latitude, longitude):
   try:
      if (float(latitude) >= -90 and float(latitude) <= 90) and (float(longitude) >= -180 and float(longitude) <= 180):
         full_location = latitude + ',' + longitude

         if re.match(pattern_location, full_location):
            update_info(latitude, longitude)
         else:
            messagebox.showerror(message="Los datos introducidos no son válidos.",title='Error al leer las coordenadas.')
      else:
         messagebox.showerror(message="El rango de los grados no es correcto.",title='Rango inválido de coordenadas.')
   except:
      messagebox.showerror(message="Los datos introducidos no son válidos.",title='Error al leer las coordenadas.')

def create_regex():
   global pattern_location

   latitude_range = '([0-9]|[1-8][0-9]|90)' # 0 a 90
   longitude_range = '([0-9]|[1-9][0-9]|[1][0-7][0-9]|180)' # 0 a 180
   decimal = '(\.\d+)?'
   minute_seconds = '([0-9]|[0-5][0-9]|60)' # 0 a 60
   latitude_DMS = '(' + latitude_range + '°' + minute_seconds + '\'' + minute_seconds + '.[\d]+"[NS])'
   longitude_DMS = '(' + longitude_range + '°' + minute_seconds + "'" + minute_seconds + '.[\d]+"[EO])'

   re_list = [
      '^' + '\-?' + latitude_range + decimal + ',\-?' + longitude_range + decimal + '$',
      '^' + latitude_DMS + '\s' + longitude_DMS + '$'
   ]

   pattern_location = re.compile(r'|'.join(re_list))

def initialize_info():
   global hti
   global geolocator

   hti = Html2Image(custom_flags=['--virtual-time-budget=2000'])
   geolocator = Nominatim(user_agent='Locations')

   create_regex()

def show_location_evaluator():
   global label_city
   global label_state
   global label_country
   global label_map
   global label_flag

   initialize_info()

   font = 'Helvetica 12'
   background = '#2A0C4E'
   frame = Frame(window, background=background)
   frame.place(relx=0.05, rely=0.05, relheight=1, relwidth=1)

   # Decimal Degree (DD) Section

   LabelFrame(frame, text='Grados Decimales (GD)', background=background, font='Helvetica 12 bold', fg='white', width=360, height=150, bd=0.5).place(x=0,y=0)
   
   Label(frame, text='Latitud:', background=background, font=font, fg='white').place(x=10,y=35)
   entry_lat = Entry(frame,width=31)
   entry_lat.place(x=80,y=33)

   Label(frame, text='Longitud:', bg=background, font=font, fg='white').place(x=10,y=70)
   entry_lon = Entry(frame,width=31)
   entry_lon.place(x=80,y=68)

   Button(frame, text='Encontrar ubicación', font='Helvetica 10', width=23, command=lambda:evaluate_location_DD(entry_lat.get(), entry_lon.get())).place(x=80,y=105)

   # Degree Minute Second (DMS) Section

   latitude_text = "Latitud:              °           '                    \""
   longitude_text = "Longitud:           °           '                    \""
   str_var1 = StringVar()
   str_var2 = StringVar()

   LabelFrame(frame, text='Grados, Minutos, Segundos (GMS)', background=background, font='Helvetica 12 bold', fg='white', width=360, height=150, bd=0.5).place(x=0,y=175)

   Label(frame, text=latitude_text, background=background, font=font, fg='white').place(x=10,y=210)

   entry_degree_lat = Entry(frame,width=4)
   entry_degree_lat.place(x=80,y=208)

   entry_minute_lat = Entry(frame,width=4)
   entry_minute_lat.place(x=130,y=208)

   entry_second_lat = Entry(frame,width=8)
   entry_second_lat.place(x=180,y=208)

   Radiobutton(frame, text='N', variable=str_var1, value='N', highlightthickness=0).place(x=262.5,y=209)
   Radiobutton(frame, text='S', variable=str_var1, value='S', highlightthickness=0).place(x=305,y=209)

   Label(frame, text=longitude_text, background=background, font=font, fg='white').place(x=10,y=245)

   entry_degree_lon = Entry(frame,width=4)
   entry_degree_lon.place(x=80,y=243)

   entry_minute_lon = Entry(frame,width=4)
   entry_minute_lon.place(x=130,y=243)

   entry_second_lon = Entry(frame,width=8)
   entry_second_lon.place(x=180,y=243)

   Radiobutton(frame, text='E', variable=str_var2, value='E', highlightthickness=0).place(x=262.5,y=244)
   Radiobutton(frame, text='O', variable=str_var2, value='O', highlightthickness=0).place(x=305,y=244)

   Button(frame, text="Encontrar ubicación", font='Helvetica 10', width=23, command=lambda:evaluate_location_DMS(entry_degree_lat.get(), entry_minute_lat.get(), entry_second_lat.get(), str_var1.get(), entry_degree_lon.get(), entry_minute_lon.get(), entry_second_lon.get(), str_var2.get())).place(x=80, y=280)

   # Location Section

   LabelFrame(frame, text='Ubicación', background=background, font='Helvetica 12 bold', fg='white', width=360, height=182.5, bd=0.5).place(x=0,y=350)

   Label(frame, text='Ciudad/Municipio/Condado', font='Helvetica 12 bold', bg=background, fg='white').place(x=10, y=375)
   label_city = Label(frame, text='', font='Helvetica 12', bg=background, fg='white')
   label_city.place(x=10, y=396)

   Label(frame, text='Estado/Región', font='Helvetica 12 bold', bg=background, fg='white').place(x=10, y=425)
   label_state = Label(frame, text='', font='Helvetica 12', bg=background, fg='white')
   label_state.place(x=10, y=447)

   Label(frame, text='País', font='Helvetica 12 bold', bg=background, fg='white').place(x=10, y=475)
   label_country = Label(frame, text='', font='Helvetica 12', bg=background, fg='white')
   label_country.place(x=10, y=498)

   # Map and flag Section

   info_img = ImageTk.PhotoImage(Image.open('info.png'))
   label_map = Label(frame, image=info_img)
   label_map.place(x=385,y=0)
   label_map.image = info_img

   label_flag = Label(frame)
   label_flag.place(x=385, y=440)

if __name__ == '__main__':
   window = Tk()
   window.title('[193269/193291] L&A.C2.A3')
   window.iconphoto(False, PhotoImage(file='icon.png'))
   window.configure(height=600, width=950, bg='#2A0C4E')
   window.resizable(False, False)
   window.eval('tk::PlaceWindow . center')

   show_location_evaluator()

   window.mainloop()