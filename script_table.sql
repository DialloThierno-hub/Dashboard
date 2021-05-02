DROP TABLE Contenir;
DROP TABLE Ecrire;
DROP TABLE Article;
DROP TABLE Mots_Cle;
DROP TABLE Auteur;
DROP TABLE Reseaux_Sociaux;
DROP TABLE Affiliation;


------------------------------ Creation de tables 

---TAble Article
CREATE TABLE Article(
                    ID_A VARCHAR(30) CONSTRAINT pk_article PRIMARY KEY,
                    Date_publi VARCHAR(15), 
                    Lien_art VARCHAR(150), --- Lien vers l'article 
                    Titre_art VARCHAR(500) ---- Titre de l'article 
    
); 
-- Table Mots_cle

CREATE TABLE Mots_Cle(
                      MotsCle VARCHAR(50) CONSTRAINT pk_mots_cle PRIMARY KEY

);

----Table Affiliation, cette table concerne le pays d'affiliation de l'auteur ou le pays au quel appartient un reseau social

CREATE TABLE Affiliation(
                        Nom_pays VARCHAR(25) CONSTRAINT pk_pays PRIMARY KEY);
        
---- Table Auteur
CREATE TABLE Auteur(
                   ID_Auteur VARCHAR(50) CONSTRAINT pk_auteur PRIMARY KEY,
                   Nom VARCHAR(50),
                   Prenom VARCHAR(50),
                   Nom_pays VARCHAR(50) CONSTRAINT fk_pays_auteur REFERENCES Affiliation(Nom_pays) ---pays d'affiliation de l'auteur 

); 
                        
------Table Reseaux Socieaux

CREATE TABLE Reseaux_Sociaux(
                             Nom_reseau VARCHAR(30) CONSTRAINT pk_reseau PRIMARY KEY,
                             Nom_pays VARCHAR(30) CONSTRAINT fk_pays_reseau REFERENCES Affiliation(Nom_pays) -- Pays d'appartenance du reseau social 

);

--- Table Ecrie 

CREATE TABLE Ecrire(
                   ID_A VARCHAR(30),
                   ID_Auteur VARCHAR(50),
                   CONSTRAINT pk_ecrire PRIMARY KEY (ID_A, ID_Auteur),
                   CONSTRAINT fk_ecrire_pays FOREIGN KEY (ID_A) REFERENCES Article(ID_A),
                   CONSTRAINT fk_ecrire_auteur FOREIGN KEY (ID_Auteur) REFERENCES Auteur(ID_Auteur)
                   
                   );
                
---tTable contenir 

CREATE TABLE Contenir(
                      MotsCle VARCHAR(50),
                      ID_A VARCHAR(30), 
                      CONSTRAINT pk_contenir PRIMARY KEY (MotsCle, ID_A),
                      CONSTRAINT fk_mots_cont FOREIGN KEY (MotsCle) REFERENCES Mots_Cle(MotsCle),
                      CONSTRAINT fk_art_cont FOREIGN KEY (ID_A) REFERENCES Article(ID_A)
);

COMMIT;

