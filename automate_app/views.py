from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PersonneForm, UploadCSVForm
from django.db import connections
from datetime import datetime
import csv
import io


def single(request):
    if request.method == "POST":
        form = PersonneForm(request.POST)
        if form.is_valid():
            print("Formulaire valide")
            try:
                nom = form.cleaned_data["nom"]
                prenom = form.cleaned_data["prenom"]
                date_naissance = form.cleaned_data["date_naissance"]
                
                # Correction du formatage de date
                date_str = date_naissance.strftime('%Y-%m-%d')

                print(f"Recherche: {prenom} {nom} née le {date_str}")  
                
                # Appel de la fonction de recherche
                resultats = rechercher_individu(nom, prenom, date_str)
                
                if resultats:
                    print(f"{len(resultats)} résultats trouvés")  
                    return render(request, "automate_app/single.html", {
                        "form": form,
                        "resultats": resultats
                    })
                else:
                    print("Aucun résultat")  
                    messages.info(request, f"Aucun résultat trouvé pour {nom} {prenom} {date_naissance}")
                    return redirect("single")  
                    
            except Exception as e:
                print(f"Erreur: {str(e)}")  
                messages.error(request, f"Erreur lors de la recherche: {str(e)}")
                return redirect("single")
    
    else:  
        form = PersonneForm()  
    
    return render(request, "automate_app/single.html", {"form": form})

def multiple(request):
    """
    Vue permettant de traiter un fichier CSV et de filtrer les résultats
    selon les critères du formulaire.
    """    
    resultats_list = []
    csvForm = UploadCSVForm()
    form = PersonneForm()

    if request.method == 'POST':
        form = PersonneForm(request.POST)
        csvForm = UploadCSVForm(request.POST, request.FILES)
        
        if csvForm.is_valid():
            try:
                # Récupération des critères de recherche s'ils sont valides
                if form.is_valid():
                    nom = form.cleaned_data.get("nom", "").lower() if form.cleaned_data.get("nom") else ""
                    prenom = form.cleaned_data.get("prenom", "").lower() if form.cleaned_data.get("prenom") else ""
                    date_naissance = form.cleaned_data.get("date_naissance")
                    
                    # Formatage de la date pour l'affichage
                    date_str = date_naissance.strftime('%Y-%m-%d') if date_naissance else ""
                    print(f"Recherche: {prenom} {nom} née le {date_str}")
                else:
                    # Si les critères ne sont pas valides, on n'applique pas de filtre
                    nom = ""
                    prenom = ""
                    date_naissance = None
                
                # Traitement du fichier CSV
                csv_file = request.FILES['fichier_csv']
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'Le fichier doit avoir une extension .csv.')
                    return render(request, "automate_app/multiple.html", {
                        "csvForm": csvForm, 
                        "form": form, 
                        "resultats_list": resultats_list
                    })
                
                messages.success(request, 'Fichier CSV téléchargé avec succès.')
                
                # Lecture du fichier en mode texte et non binaire
                file_data = csv_file.read().decode('utf-8')
                csv_data = io.StringIO(file_data)
                
                # Utilisation du module CSV pour parser le fichier
                reader = csv.DictReader(csv_data)
                
                # Traitement des lignes du CSV
                for row in reader:
                    try:
                        # Extraction et nettoyage des données de la ligne
                        nom_csv = row.get('nom', '').strip().lower() if row.get('nom') else ''
                        prenom_csv = row.get('prenom', '').strip().lower() if row.get('prenom') else ''
                        date_csv_str = row.get('date_naissance', '')
                        
                        # Conversion de la date
                        date_csv = None
                        if date_csv_str:
                            try:
                                date_csv = datetime.strptime(date_csv_str, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                # Si la conversion échoue, on laisse date_csv à None
                                pass
                        
                        # Vérification des critères de correspondance
                        match_nom = not nom or (nom_csv == nom)
                        match_prenom = not prenom or (prenom_csv == prenom)
                        match_date = not date_naissance or (date_csv == date_naissance)
                        
                        # Si tous les critères correspondent, on ajoute la ligne aux résultats
                        if match_nom and match_prenom and match_date:
                            resultats_list.append(row)
                            
                    except Exception as e:
                        messages.error(request, f"Erreur lors du traitement de la ligne {row}: {str(e)}")

                return render(request, "automate_app/multiple.html", {
                        "csvForm": csvForm, 
                        "form": form, 
                        "resultats_list": resultats_list
                    }
                )          
            except Exception as e:
                messages.error(request, f"Erreur générale: {str(e)}")
    
    # Rendu de la page avec contexte
    return render(request, "automate_app/multiple.html", {
        "csvForm": csvForm, 
        "form": form, 
        "resultats_list": resultats_list
    })


def rechercher_individu(nom, prenom, date_naissance):

    try:
        with connections['mariadb'].cursor() as cursor:
            print("connexion")
            query = """
                SELECT * FROM personnes 
                WHERE nom = %s AND prenom = %s AND date_naissance = %s
            """
            print("execution")
            cursor.execute(query, [nom, prenom, date_naissance])
            print("exécuté")
            
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
    except Exception as e:
        print(f"Erreur DB: {str(e)}")  
        raise