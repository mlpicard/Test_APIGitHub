# Test_APIGitHub

### Configuration du serveur Apache :
Pour exécuter l'interface en local via un serveur Apache :
  - modifier le fichier httpd.conf (présent dans le dossier conf de Apache) de façon à avoir les liens correspondant au dossier cgi-bin de Apache. Exemple des parties du fichier httpd.conf à modifier :
    ```
    ScriptAlias /cgi-bin/ "C:/Program Files (x86)/Apache Software Foundation/Apache2.2/cgi-bin/"

    <Directory "C:/Program Files (x86)/Apache Software Foundation/Apache2.2/cgi-bin">
      AllowOverride None
      Options None
      Order allow,deny
      Allow from all
    </Directory>
    ```

  - placer le fichier test.cgi dans le dossier cgi-bin de Apache
  - placer les fichiers style.css et test.html dans le dossier htdocs
  
  Ensuite en tapant localhost/test.html dans le navigateur l'interface s'affichera.
