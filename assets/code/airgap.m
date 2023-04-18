clc; clear all; close all;
%Data récupérer de BP
datamm = [1.0 1.5	2.0	3.0	4.0];
datamm_2 = [1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0 17.0 18.0 19.0 20.0];
dataG = [1742 1376 1028 704 454];

degre_modele = 3;

p = polyfit(datamm,dataG,degre_modele);

figure(1)
predict = polyval(p, datamm)
plot(datamm,dataG,datamm,predict,'LineWidth',2)
xlim([1.0 4])
ylim([0 inf])
xlabel('mm')
ylabel("Gauss")
grid on
legend('Données','Modèle','location','northeast')
title("Intensité du champ magnétique en fonction de l'airgap")

figure(2);
predict = polyval(p, datamm_2)
plot(datamm,dataG,datamm_2,predict,'LineWidth',2)
xlim([1.0 10.0])
ylim([0 inf])
xlabel('mm')
ylabel("Gauss")
grid on
legend('Données','Prédiction','location','northeast')
title("Intensité du champ magnétique en fonction de l'airgap")