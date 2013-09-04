all: bench-c bench-s

bench-c: memset.c harness.c
	${CC} ${CFLAGS} -o bench-c memset.c harness.c

bench-s: memset.S harness.c
	${CC} ${CFLAGS} -o bench-s memset.S harness.c

clean:
	-rm bench-[cs]
