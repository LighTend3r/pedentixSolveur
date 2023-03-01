from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import json
import bs4
"""
pip install selenium
pip install webdriver-manager
pip install tqdm
pip install requests
pip install bs4

MOD 1000 mot
MOD 10000 mot
MOD ALL   

MOD partage
MOD non partage

MOD Firefox
MOD Chrome
MOD Edge
MOD Opera
MOD Brave

MOD after
MOD during

MOD thread <nb>
"""

URL_PEDANTIX_FORM = "https://cemantix.certitudes.org/pedantix/score"
URL_PEDANTIX = "https://cemantix.certitudes.org/pedantix"
SESSION = requests.session()

def motValide(mot):
    headers = {'content-type': 'application/json'}
    data = {"word":mot,"answer":[mot,mot]}
    try:
        r = SESSION.post(URL_PEDANTIX_FORM, data=json.dumps(data), headers=headers)
    except Exception:
        print("[-] Erreur lors de la requête")
        print("[-] Vérifiez votre connexion internet"
              " ou si le site https://cemantix.certitudes.org/ est accessible")
        return None

    return r.json()

def main():
    print("[+] Initialisation")
    listeMotValide = []
    listeTitre = []
    dicPhraseATrouver = {}
    phraseATrouver = ""

    
    try:
        r = SESSION.get(URL_PEDANTIX)
    except Exception:
        print("[-] Erreur lors de la requête")
        print("[-] Vérifiez votre connexion internet"
              " ou si le site https://cemantix.certitudes.org/ est accessible")
        return
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    div_game = soup.find('div', {'class': 'game'})
    h2 = div_game.find('h2')
    nbATrouver = 0

    for i in h2:
        if "span" in str(i):
            phraseATrouver += f"{i.get('id')} "
            dicPhraseATrouver[i.get('id')] = f"{str(len(i.text) - 2)}"
            nbATrouver += 1
        else:
            phraseATrouver += f"{i.text.strip()} "
    print()
    print("[+] Nombre de mots à trouver (dans le titre): ", nbATrouver)
    print("[+] Phrase à trouver: ", phraseATrouver)

    print("\n[+] Brute force du titre")
    print()

    phraseATrouver, nbATrouver = header(listeTitre, dicPhraseATrouver, phraseATrouver, nbATrouver)

    if nbATrouver == 0:
        print(f"[+] Titre trouvé : {phraseATrouver}")
        browser(listeTitre)
        return

    print()
    print("[-] Nous n'avons pas réussi à trouver le titre")
    print("[-] Nous allons donc lancer le brute force sur tout le texte")
    print()

    print("[+] Chargement du dictionnaire...")

    with open('dict\\dict.txt', 'r',encoding='utf-8') as f:
        t = f.readlines()
        print("[+] Dictionnaire chargé !")
        print("[+] Traitement des mots...")
        print()
        for nb, mot in enumerate(t, start=1):
            mot = mot.replace('\n','').lower()
            retour = motValide(mot)
            if retour is None:
                return
            if retour != {}:
                listeMotValide.append(mot)

            if nb % 1000 == 0:
                print(f"{str(round(nb / len(t) * 100, 2))}%")

    print()
    print("[+] Mots traités !")
    print()

    # Lancement du navigateur
    browser(listeMotValide)

    return

def header(listeTitre, dicPhraseATrouver, phraseATrouver, nbATrouver):
    for id in dicPhraseATrouver.keys():
        found = False
        if not 0 < int(dicPhraseATrouver[id]) < 22:
            print("[-] Mot non trouvé, id:", id)
            continue

        with open(f'dict\\dict{str(dicPhraseATrouver[id])}.txt', 'r', encoding='utf-8') as f:
            t = f.readlines()
            for mot in t:
                mot = mot.replace('\n','').lower()
                r = motValide(mot)
                if str(id) in r["score"].keys() and r["score"][str(id)].lower() == mot:
                    print("[+] Mot trouvé: ", mot)
                    phraseATrouver = phraseATrouver.replace(id, mot)
                    print("[+] Phrase à trouver: ", phraseATrouver)
                    nbATrouver -= 1
                    listeTitre.append(mot)
                    found = True
                    break
        if not found:
            print("[-] Mot non trouvé, id:", id)
        print()        
    return phraseATrouver, nbATrouver


def browser(listeMotValide):
    print("[+] Lancement du navigateur...")
    try:
        options = Options()
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        driver.get(URL_PEDANTIX)
        driver.maximize_window()
    except Exception:
        print("[-] Erreur lors du lancement du navigateur")
        print("[-] Vérifiez que le driver de Chrome est bien installé")        
        return
    
    print("[+] Navigateur lancé !")

    # Fermeture de la popup
    a_elt = driver.find_element(By.ID, "dialog-close")
    a_elt.click()

    # Récupération des éléments
    input_elt = driver.find_element(By.ID, "pedantix-guess")
    form_elt = driver.find_element(By.ID, "pedantix-form")
    print()
    print("[+] Envoi des mots...")
    # Envoi des mots
    for mot in listeMotValide:
        input_elt.clear()
        input_elt.send_keys(mot)
        form_elt.submit()
    print("[+] Mots envoyés !")

if __name__ == "__main__":
    main()
