#include <stdio.h>
#include <stdlib.h>
#include <conio.h>

int main(){
  enum transport {car, train, airplane, bus} tp;
  int rob, i;
  printf("Press a key to select transport: ");

  // generate a new random number each time the program is run
 for( i=0; i<10; i++){  
  while(!kbhit()) rand();  //funkcja kbhit() czeka a¿ zostanie naciœniêty dowolny klawisz
  getch(); // funkcja getch() wczytuje znak, ale go nie wyœwietla

  rob = rand() % 4;
  tp=(enum transport)rob;
  switch(tp) {
    case car: printf("\ncar");
      break;
    case train: printf("\ntrain");
      break;
    case airplane: printf("\nairplane");
      break;
    case bus: printf("\nbus");
  }
 }
  getche();
  return 0;
}
