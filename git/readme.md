This folder contains stuff specific to git

e.g. if you are contributing to this project you should link the git hooks on your system.

```
cd <rfswarm>/.git/hooks
ln -s ../../git/hooks-bash/post-commit
ln -s ../../git/hooks-bash/post-commit post-merge
ln -s ../../git/hooks-bash/post-commit post-checkout
```
