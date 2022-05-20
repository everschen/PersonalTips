#include <stdio.h>
#include <stdlib.h>

int main()
{
    printf("Hello World");

    int i=0, j=0;
    while(1)
    {
        void *p=malloc(1024*1024);
        i++;
        if (p)
        {
            printf("success to allocate i=%d\n", i);
        }
        else
        {
            printf("failed to allocate i=%d\n", i);
            j++;
            if (j==5)
                 break;
        }
        //usleep(10000);
    }

    return 0;
}

