import argparse
import threading
import os
import time
import requests
import sys
from termcolor import colored

#burası kodu çalıştırırken parametre vermemizi sağlıycak
parser = argparse.ArgumentParser(description='sitedeki gizli dizinleri bulun',usage="tool kullanım rehberi")
parser.add_argument("-s", "--site", metavar="", type=str, help="site adını gir (başında http/https olmadan)",required=True)
parser.add_argument("-t", "--txt",metavar="" ,type=str, help="\" \" işaretleri içine txt dosyasının tam yolunu gir (girmezseniz githubdan bir liste çekilir ve o liste ile deneme yapılır)")
parser.add_argument("-fv", "--FormVerileri",metavar="" ,nargs="+", help='(login olmadan alt sayfalarda gezinemediğiniz siteler için) form verilerini boşluklu bir şekilde girin örneğin : login=ahmet password=sifre123')

args = parser.parse_args()
uzantılar = [".php",".js",".html",".css",".org",".com",".txt",".pdf",".zip"] #aşağıda bu uzantıları tek tek deniycez kodun [110]   [142] sıralarında kullanımı mevcut

if args.txt: #eğer -t veya --txt ile bir txt yolu belirtildiyse 
    try:        
        txt = open(args.txt,"r").read() #txt'yi okuma modunda açıyoruz ve txt adlı değişkene atıyoruz
    except:
        #burası hata durumunda çalışır büyük ihtimalle kullanıcı yanlış bir yol girdi
        print("txt yolunu kontrol et ve \" \" işaretleri arasında gir")
        sys.exit(1) #çıkış yapıyoruz

else: # txt yolu belirtilmediyse githubdan liste çekicez
    github = "https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-medium.txt" 
    txt = requests.get(github).text # github'dan orta seviye bir wordlist çekiyoruz
print(
"""
Gizli Dizinleri Bulacağımız Site

1) http ile başlıyor
2) https ile başlıyor
"""
)
while True:
    try:
        soru = int(input())
        break
    except ValueError:
        print("int bir değer girin")

#sistem windows ise cls linux ise clear komutu çalışacak
if os.name == 'nt':
    os.system("cls")
else:
    os.system("clear")

başlangıc = ""
if soru == 1:
    başlangıc = "http://"
elif soru == 2:
    başlangıc = "https://"
else:
    print("1 veya 2 değerini girin")

url = başlangıc+args.site #seçilen url başlangıcı ile -s --site değerine verilen siteyi birleştiriyoruz
içerik = requests.get(url)

ana_sayfa = içerik.text #sitenin içeriğini alıyoruz
hatalı_sayfa = requests.get(url+"/wikl4ggaaaa").text # sitenin hata veren çıktısını alıyoruz

dizinler = txt.splitlines() # alt alta gelen satırları splitlines ile parçalayıp bir liste haline getiriyoruz

süre = içerik.elapsed.total_seconds() #elapsed.total_seconds() bize ne kadar sürede siteye değer gönderip cevap alabildiğimizi belirtir bu sayede kullanıcıya kodun ne kadar sürede biteceğini haber verebiliriz
zaman = str((len(dizinler)*süre)/60)
zaman = zaman.split(".")[0]

print(f"taramanın ortalama bitme süresi : {(int(zaman)*int(len(uzantılar)+1))+1} dakika")
def bul():
    print(colored("\nbulunan dizinler mavi renkte gösterilecektir","blue")) #colored adlı modül ile renkli çıktılar verebiliriz ("metin","renk")
    print(colored("dosya olduğu tahmin edilenler kırmızı renkte gösterilecektir NOT dizin olma ihtimalide var\n","red"))
    
    if args.FormVerileri: # -fv veya --FormVerileri parametresi secilip değerler girildi ise işlemlerimizi login olup gerçekleştiricez girilmediyse 124'üncü satırdan devam edicek kod
        
        data = args.FormVerileri #verilen name=ahmet password=123 gibi değerleri data'ya aktarıyoruz
        sözlük = {}
        
        for i in range(len(data)):
            
            key,value = str(data[i]).split("=") #name=ahmet ifadesini = işaretinden parçalıyoruz ve name değeri key'in içine gidiyor ahmet ifadesi value içine gidiyor
            if i == len(data)-1: #kullanıcı -h veya --help parametresini kullanıp (site değerini en sona gir) mesajımızı görmüştü ve kullanıcıda siteyi en sona girmişti 
                #ve eğer data'daki son değere geldiysek son değeri login_sayfası adlı değişkene atıyoruz
                login_sayfası = value
            else:
                sözlük[key] = value
        
        session = requests.Session() #oturum nesnesi oluşturuyoruz bu nesne sayesinde siteye login olduktan sonra birdaha login olmamıza gerek kalmayacak ve sitenin alt sayfaları ile etkileşim kurabilecez
        session.post(login_sayfası,data=sözlük) #kullanıcının girdiği form verilerini login sayfasına gönderiyoruz ve login oluyoruz
        
        for i in dizinler: 
            if str(i).startswith("/") or str(url).endswith("/"): #deneyeceğimiz değerler / ile başlıyorsa yada url / ile bitiyorsa herhangi bir işaret eklemiyoruz
                i = f"{url}{i}"
            else: # deneyecegimiz degerler / ile başlamıyorsa / ekliyoruz
                i = f"{url}/{i}"
        
            içerik = session.get(i)
            durum_kodu = içerik.ok # ok ne işe yarar? : durum kodu 400'den düşük değerleri True olarak döndürür #buna status code nedir 400'ün yukarısındaki değerler hatalı demektir onun altındakiler bizim işimizi görecek
            denenen_sayfa = içerik.text #denediğimiz gizli dizinin içeriği
            time.sleep(0.50) #yarım saniye bekliyoruz

            if denenen_sayfa != ana_sayfa and denenen_sayfa != hatalı_sayfa and durum_kodu and içerik.url == i:
    
                print(colored(f"[+] : {i}","blue"))  #varolan dizini mavi renkte yazdırıyoruz
                
            #---dosya kısmı--- txt dosyası verilen veya githubdan çekilen dizinlerin sonuna .zip .php .txt gibi uzantılar eklenecektir
            if i.endswith("/"):     #sonda / işareti varsa kaldırıyoruz çünkü dosya ekliycez
                i = i.replace(i[-1:],"")
            for t in uzantılar:
                            
                dosya = i+t #dosya uzantısını ekleyip deniyoruz
                try:
                    içerik = session.get(dosya)
                except:
                    continue
                dosya_kodu = içerik.ok # durum kodu 400'den küçükse True döndürür
                denenen_dosya = içerik.text #denediğimiz gizli dizinin içeriği
                time.sleep(0.50) #yarım saniye bekle
                
                if denenen_dosya != ana_sayfa and denenen_dosya != hatalı_sayfa and dosya_kodu and içerik.url == dosya and denenen_dosya != denenen_sayfa:
                    print(colored(f"[+] : {dosya}","red")) #varolan dosyayı kırmızı renkte yazdırıyoruz     
    
    else: #---login olma işlemi seçilmediyse---
        for i in dizinler: 
            if str(i).startswith("/") or str(url).endswith("/"): #deneyeceğimiz değerler / ile başlıyorsa yada url / ile bitiyorsa herhangi bir işaret eklemiyoruz
                i = f"{url}{i}"
            else:
                i = f"{url}/{i}" # eğer arada / işareti yoksa araya / işareti ekliyoruz

            içerik = requests.get(i)
            durum_kodu = içerik.ok # ok = durum kodu 400'den düşükse True değeri döndürür 
            denenen_sayfa = içerik.text #sayfa içeriği
            time.sleep(0.50) #yarım saniye bekle
            
            if denenen_sayfa != ana_sayfa and denenen_sayfa != hatalı_sayfa and durum_kodu and içerik.url == i:
                print(colored(f"[+] : {i}","blue")) #varolan dizini mavi renkte yazdırıyoruz
                        
            #---dosya kısmı--- txt dosyası verilen veya githubdan çekilen dizinlerin sonuna .zip .php .txt gibi uzantılar eklenecektir
            if i.endswith("/"):
                    i = i.replace(i[-1:],"") # dosya eklemek için sonda  / işareti varsa kaldırıyoruz
            for t in uzantılar:    
                                
                dosya = i+t #linke uzantıları tek tek ekliyoruz
                try:
                    içerik = requests.get(dosya) 
                except:
                    pass
                dosya_kodu = içerik.ok #400 den düşük değerler true döndürür
                denenen_dosya = içerik.text #sayfa içeriği 
                time.sleep(0.50) #yarım saniye bekle 

                if denenen_dosya != ana_sayfa and denenen_dosya != hatalı_sayfa and dosya_kodu and içerik.url == dosya and denenen_dosya != denenen_sayfa:
                    print(f"[+] : {dosya}","red") #varolan dosyayı kırmızı renkte yazdırıyoruz
                
t = threading.Thread(target=bul) #buda kodun hızlı çalışması için
t.start()
