% Calcul de la DFT 
A = 1 ; 
K = 3*N ; % Changer K pour la resolution 
Fd =(0:1:K-1) ;
Fd = Fd*(Fe/K) ;
X = zeros(1,length(Fd)) ;
pi  = sym(pi) ; % Definition exacte de pi  
for k = 0:1:K-1
    

    X(k+1) = A*sin(pi*N*(k/K))./(sin(pi*(k/K)));

    
end 

    figure(2)
    stem(Fd,abs(X))
    grid on 
    
  % Spectre periodique de Fe , discretisé en frequence d'un pas de Fe/K 