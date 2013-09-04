/*
 * See how many buffers we can set in a given number of seconds
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <err.h>
#include <signal.h>
#include <assert.h>

#include "memset1.h"

#define HOWLONG		5
#define SETCHAR		'x'
#define WARMUP_ITERS	65536

int			again = 1;

void
sig_hndl(int sig)
{
	again = 0;
}

int
main(int argc, char **argv)
{
	char			*buf;
	unsigned long long	n_bufs = 0, bufsz, i, j;

	if (argc != 2) {
		printf("usage: bench-[sc] <bufsz>\n");
		exit(EXIT_FAILURE);
	}

	bufsz = atoi(argv[1]);
	if ((buf = malloc(bufsz)) == NULL)
		err(EXIT_FAILURE, "malloc");

	/*
	 * First we check memset does what it should and warm up
	 * the cache.
	 */
	fprintf(stderr, "Warming up...\n");
	for (i = 0; i < WARMUP_ITERS; i++) {
		memset1(buf, SETCHAR, bufsz);

		for (j = 0; j < bufsz; j++)
			assert(buf[j] == SETCHAR);
	}

	/*
	 * Now we benchmark.
	 *
	 * Set up a timer.
	 * Signals are rough, but should be fine
	 */
	fprintf(stderr, "Benchmarking...\n");
	if (signal(SIGALRM, sig_hndl) == SIG_ERR)
		err(EXIT_FAILURE, "signal");

	if (alarm(HOWLONG) < 0)
		err(EXIT_FAILURE, "alarm");

	while (again) {
		memset1(buf, SETCHAR, bufsz);
		n_bufs++;
	}

	fprintf(stderr, "Done...\n");
	printf("%llu\n", n_bufs);

	return (EXIT_SUCCESS);
}
