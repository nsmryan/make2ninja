# make2ninja
This repository contains a tool for converting [Makefile](https://www.gnu.org/software/make/manual/make.html)
builds into [Ninja](https://ninja-build.org/) builds, with the
intent of speeding up a build.

I've found that it decreased the build time of the software I was
working on by 10% for a full rebuild, and 30% for a single file
change. That software has a pretty flat build tree, and a single
Makefile, so I expect greater speedups are possible for some
systems.

Already this is a pretty nice improvement- its a tiny little
script that didn't take much time to create, and I get a bit
faster builds! No complaints here.


The inspiration for this tool was https://github.com/lindenb/makefile2graph,
which parses the result of:
```bash
make -Bnd
```
to create a graph of a make build's dependencies. It was simple
to parse the output, and then generate a Ninja file instead.


The current implementation is very raw- it is the code I got
working while thinking through this idea.

## Usage
Simply try
```bash
make -Bnd | python make2ninja.py > build.ninja
```
to generate a build.ninja file.

Multiple ninja files could be created for different make builds-
ninja is more explicit, so certain make builds may result in different
ninja files (like release vs debug).


## Special Cases
I'm sure there are many special cases in Makefiles that I could have
missed. The one that make2ninja does handle is where files are given
without paths, and are resolved by VPATH (which I make use of
a great deal in Makefiles).

## Possible Improvements
This tool could detect .d files in the rules, and add the 'dep'
and 'depfile' variables to its output.


It could also just be written in a clearer and more organized fashion-
its just a proof of concept right now.

In prinicpal something could be done to detect changes in the build to
regenerate the file, or incorporate this tool into the make file to
regenerate the ninja file somehow. I haven't thought this one through
entirely.


Please feel free to fork, PR, or make an issue if this is an interesting
or useful tool!


