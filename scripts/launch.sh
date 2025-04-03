cd /BentoClip/
bentoml serve -p 3000 . > /dev/null 2>&1 &
cd /BentoSDXLTurbo/
bentoml serve -p 4000 . > /dev/null 2>&1 &