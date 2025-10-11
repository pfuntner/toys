# I've moved!

Welcome weary traveler!  Thanks for visiting my repository.

I've been disturbed by [potential misuse of my creations by the owners of Github](https://www.theverge.com/news/757461/microsoft-github-thomas-dohmke-resignation-coreai-team-transition) so I've decided to migrate my repos to [Codeberg](codeberg.org).  If you have repositories too, I encourage you to consider if you want to stay with Github.  There are several alternatives!  You'll continue to use the good old `git` CLI in your shell and IDEs but the backend is different.

## Welcome to Codeberg
My repository is still alive and well at https://codeberg.org/mrbruno/toys.  I have no intention to decrease my contributions to the repository - I literally _eat my own dog food_!  Many of these tools are important to me because I often use them.

You can continue to use my repo by updating the remote URL (this is what I've been doing to my clones):
```
cd toys
git remote set-url origin https://codeberg.org/mrbruno/toys.git
git pull # not necessary but will test that the repo is set up right
```

If you rather, you can just remove the entire tree and just clone it again:
```
cd toys/..
rm -rf toys
git clone https://codeberg.org/mrbruno/toys.git
```

## Migrating
I'm not going to try to convince you that you should migrate your own Github repos to Codeberg too but it's a choice and it's where I landed.  I will tell you that it's been easy to migrate my repos.  Yes, things are different and I have a little more learning to do but I'm confident enough to migrate this major repo of mine.  It took me a little to figure out how to do a webpage but it wasn't too difficult.

I have not found a Codeberg replacement for [Gist](https://gist.github.com/) yet - maybe I just haven't looked hard enough or in the right place.  It's not hard to find other Gist alternatives but I haven't checked any of them out yet.
