#include <sys/param.h>
#include <sys/types.h>
#include <sys/socket.h>

#include <getopt.h>
#include <malloc_np.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <sysexits.h>
#include <unistd.h>

main()
{
unsigned int narenas;
bool retain;

size_t narenas_len = sizeof(narenas);
size_t retain_len = sizeof(retain);

mallctl("opt.narenas", &narenas, &narenas_len, NULL, 0);
mallctl("opt.retain", &retain, &retain_len, NULL, 0);

printf("opt.narenas=%d\n", narenas);
printf("opt.retain=%d\n", retain);

mallctl("arenas.narenas", &narenas, &narenas_len, NULL, 0);
printf("arenas.narenas=%d\n", narenas);

}

