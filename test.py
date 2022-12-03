def fonction_liste_minerais(continent):
    liste_minerais_courant = {
        'pierre': 0,
        'gravier': 0,
        'calcaire': 0,
        'charbon': 1,
        'aluminium': 1,
        'plomb': 1,
        'cuivre': 1,
        'fer': 2,
        'étain': 2,
        'zinc': 2,
        'nickel': 2,
        'or': 3,
        'cobalt': 3,
        'platine': 3,
        'uranium': 5,
        'diamant': 6,
        
    }
    if continent == 1:
        pass
    elif continent == 2:
        pass
continent = int(input("Continent (1 / 2): "))
height = int(input("Hauteur: "))
while True:
    rarity = input("Spécifier la rareté (écrivez 'liste' pour obtenir la liste des matériaux):")
    if type(rarity) is str:
        if rarity.lower() == "liste":
            fonction_liste_minerais(continent=continent)
        else:
            print("Erreur !")