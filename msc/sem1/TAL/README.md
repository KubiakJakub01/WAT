# Techniki algorytmiczne

Problem: Euklidesowy problem komiwojażera (Algorytm genetyczny)

## Problem komiwojażera

Zacznijmy od problemu komiwojażera (Traveling Salesman Problem, TSP). Problem ten jest prosty do zdefiniowania: Wyobraźmy sobie sprzedawcę, który musi odwiedzić zestaw miast dokładnie raz, a następnie wrócić do punktu początkowego. Celem jest znalezienie najkrótszej możliwej trasy, która wykona to zadanie. Jednak to, co sprawia, że TSP stanowi wyzwanie, to fakt, że liczba możliwych tras rośnie wraz ze wzrostem liczby miast. Ta złożoność sprawia, że TSP jest problemem NP-trudnym, co oznacza, że nie jest znany skuteczny sposób na zagwarantowanie optymalnego rozwiązania dla dużych zbiorów danych. Pomimo swojej złożoności, TSP ma wiele rzeczywistych zastosowań, w tym w logistyce, planowaniu tras i projektowaniu sieci. Zrozumienie i rozwiązanie TSP może prowadzić do znacznej poprawy wydajności w tych dziedzinach.

## Algorytmy genetyczne

Przyjrzyjmy się teraz, w jaki sposób algorytmy genetyczne (GA) umożliwiają rozwiązywanie złożonych problemów optymalizacyjnych, takich jak TSP. GA są inspirowane zasadami naturalnej ewolucji. Opierają się one na populacjach potencjalnych rozwiązań - zwanych chromosomami - które ewoluują w czasie. Proces rozpoczyna się od populacji początkowej, w której każdy chromosom reprezentuje możliwe rozwiązanie - w tym przypadku trasę przez wszystkie miasta. Funkcja dopasowania ocenia jakość każdej trasy na podstawie całkowitej odległości, przy czym krótsze trasy są „dopasowane”. GA wykorzystuje selekcję do wyboru najlepszych tras do reprodukcji, krzyżowanie do łączenia tras rodzicielskich w nowe potomstwo oraz mutację do wprowadzania niewielkich zmian i utrzymywania różnorodności. Celem jest poprawa populacji w kolejnych pokoleniach, zbiegając w kierunku optymalnego lub prawie optymalnego rozwiązania.

## Zastosowanie algorytmów genetycznych w problemie komiwojażera​

Na koniec zobaczmy, w jaki sposób GA są konkretnie stosowane w problemie komiwojażera. Trasy są zakodowane jako chromosomy, z których każdy reprezentuje unikalną sekwencję miast. Aby wygenerować nowe rozwiązania, używamy wyspecjalizowanych operatorów. Na przykład operatory krzyżowania, takie jak Order Crossover, łączą trasy od rodziców, zapewniając prawidłowe sekwencje miast. Operacje mutacji, takie jak zamiana dwóch miast lub odwrócenie sekcji trasy, wprowadzają zmienność i pomagają uniknąć lokalnych optimów. GA są potężne, ponieważ dobrze radzą sobie z dużymi przestrzeniami wyszukiwania, często znajdując dobre rozwiązania szybciej niż metody dokładne. Wiąże się to jednak z wyzwaniami, takimi jak dostrajanie parametrów - takich jak szybkość mutacji - i zapewnienie, że algorytm nie utknie w nieoptymalnych rozwiązaniach. Ogólnie rzecz biorąc, GA oferują elastyczne i skuteczne podejście do rozwiązywania TSP.
