#include <stdlib.h>
#include <stdio.h>

int main(void) {
    long total = 0;
    long page = 4096;
    while (total < 4L<<30) {
        malloc(page);
	    total += page;
        printf ("memory: %ld MB\n", total >> 20 );
    }
    printf("sleeping ...");
    sleep(9999999);
}
