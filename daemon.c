/*
    gcc -std=c89 -static -o daemon daemon.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>

void main(int argc, char *argv[]) {
    if (argc <= 1) {
        fprintf(stderr, "Not enough arguments to proceed\n");
        exit(EXIT_FAILURE);
    }

    pid_t pid, sid;
    int i;

    pid = fork();
    if (pid < 0 || pid > 0) exit(EXIT_FAILURE);

    /* create new session for child */
    sid = setsid();
    if (sid < 0) exit(EXIT_FAILURE);

    signal(SIGCHLD, SIG_IGN);
    signal(SIGHUP, SIG_IGN);

    pid = fork();
    if (pid < 0 || pid > 0) exit(EXIT_FAILURE);

    /* file mask */
    umask(0);

    /* change directory */
    if (chdir("/") < 0) exit(EXIT_FAILURE);

    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    char *argv0[argc-1];
    for (i=1; i<argc; i++) {
        argv0[i-1] = argv[i];
    }
    execvp(argv[0], argv0);
}

