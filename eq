[33mcommit 73d5bb1f11dbabc9a3a8abd6fcc617acb0d5c93c[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 17 18:03:59 2017 +0100

    Improved the saving speed by saving in chunks of data instead of single images. Improved the quitting mechanisms

[33mcommit 4309693bd0aedce81a1f0d27601973b36c943317[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 17 16:54:22 2017 +0100

    Solved problem with parallel process for saving data. I was importing a module instead of a function and that was giving Pickle errors

[33mcommit 7ce00b3fb61bcce0f93352e20ac248610d0e5f84[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 17 16:19:15 2017 +0100

    Problems with SaverWorker

[33mcommit bdbdcc9a6d2efbeb151ad234c9271d07cf4f2f42[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 17 14:51:05 2017 +0100

    Cleaned up the view directory

[33mcommit f7f11218793792780d2faf570e627bd6f5240e45[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 17 14:50:46 2017 +0100

    Improvements to _session.

[33mcommit 88ae35867fe1cc3d9b439a23f43ada727d37c7c7[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 16 17:49:21 2017 +0100

    Oscilloscope some changes

[33mcommit 6a9c761459fb0504920776e65a9b215da3423de2[m
Merge: 7b36863 24975d7
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 16 15:02:59 2017 +0100

    Merge branch 'develop' into oscilloscope

[33mcommit 24975d79bbe265aa198aa3e118fe8f8a486622f6[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 16 15:01:11 2017 +0100

    Hamamatsu acquires something

[33mcommit 7ef88eca4d6b745f7b90ec354ed09950ecb35132[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 16 11:02:20 2017 +0100

    More clever start of the program

[33mcommit 787756010638a0531b1a304d5d9684aa56940179[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 16 10:58:09 2017 +0100

    Finished including Hamamatsu

[33mcommit 554fe4eab717735278d4007f247ccee05c902ede[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Tue Mar 14 18:10:21 2017 +0100

    Params now show up. Improved the handling in the _session class, and sync between ROI update and _session values

[33mcommit 87219917cf3d372d020e225ee1199c7b51f90b35[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Tue Mar 14 15:01:34 2017 +0100

    Solved some issues with _session. Added requirements

[33mcommit 21b3a9d39c37a9574f9c765ee0fc217156a60b0d[m
Merge: 3e61fab 0b485ec
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Tue Mar 7 18:07:18 2017 +0100

    Merged from develop

[33mcommit 0b485ec30c20f5ff5ccdd3d1092ca21e807da245[m
Merge: d222f41 1909516
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Tue Mar 7 18:06:00 2017 +0100

    Merge branch 'master' into develop

[33mcommit 7b36863a8e6fea03a8c9fe92ab4aa8fd847c7a67[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Tue Mar 7 18:03:37 2017 +0100

    Very basic start FuncGen

[33mcommit 3e61fababaa092e676bb8165999f9fd2f642077f[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Tue Mar 7 17:10:16 2017 +0100

    Small changes

[33mcommit 19095163b9089fd35c7662b01074c71f7f317f6a[m
Author: LabAdmin <LabAdmin>
Date:   Tue Mar 7 16:41:23 2017 +0100

    Updated controller of Hamamatsu camera to work on Py3

[33mcommit 2498851056639df7d4459f7670576b797f560619[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 3 19:12:25 2017 +0100

    Mayor improvement session class, solved some GUI issues

[33mcommit 9f595d0aa57562f149d04243311378357a127c78[m
Merge: 72fccbb d222f41
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 3 16:43:23 2017 +0100

    Merge branch 'develop' into docklayout

[33mcommit d222f414c8e8849b79c01b909352d026f8e4be10[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 3 16:41:19 2017 +0100

    solved crosshair

[33mcommit 72fccbb2beec9cb8cb20eb93506e6311c07fe700[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Fri Mar 3 15:13:41 2017 +0100

    Improving docks

[33mcommit 0fee508fb4da0a0fce1dc8add9675ffcf835a8db[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 2 18:19:39 2017 +0100

    Initial layout with docks

[33mcommit 867aeef334e77a9d8ab3a7373bf9b69003cbc866[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 2 18:06:44 2017 +0100

    Work on the layour

[33mcommit 71e380f1fa4b89139ea5d7d97321c5df8cff5eec[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Thu Mar 2 11:35:32 2017 +0100

    Updated readme with future tasks to be completed

[33mcommit 55190f0a2a735c2eb817ee43fab67e3314322bb5[m
Author: Aquiles Carattino <aquiles@aquicarattino.com>
Date:   Wed Mar 1 15:06:49 2017 +0100

    Minimal working example of a Camera GUI with some mouse interactions
