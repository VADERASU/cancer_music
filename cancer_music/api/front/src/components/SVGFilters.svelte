<script>
    export let id;
</script>

<filter
    id={`${id}_filter`}
    filterUnits="objectBoundingBox"
    primitiveUnits="userSpaceOnUse"
>
    <feGaussianBlur id={`${id}_blur`} stdDeviation="0" result="blurred" />
    <feMorphology
        id={`${id}_erode`}
        operator="erode"
        radius="0 0"
        in="blurred"
        result="morphology"
    />
    <feDropShadow
        id={`${id}_shadow`}
        stdDeviation="0 0"
        dx="0"
        dy="0"
        in="morphology"
        result="shadow"
    />
    <feTurbulence
        id={`${id}_turbulence`}
        baseFrequency="0.1 0.05"
        numOctaves="2"
        seed="2"
        result="turbulence"
    />
    <feDisplacementMap
        id={`${id}_displacement`}
        in="shadow"
        in2="turbulence"
        scale="0"
        xChannelSelector="G"
        yChannelSelector="A"
        result="dp"
    />
</filter>
