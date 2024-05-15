import React, { useEffect, useState, useRef } from 'react';
// @ts-ignore
import geo from "geojs";
import {monitorEventLoopDelay} from "node:perf_hooks";

const WsiView = () => {
    const viewRef = useRef(null);
    const [mode, setMode] = useState('polygon');

    function getRandomInt(min: number, max: number) {
        min = Math.ceil(min); // Ensures the minimum is rounded up to the nearest integer
        max = Math.floor(max); // Ensures the maximum is rounded down to the nearest integer
        return Math.floor(Math.random() * (max - min) + min); // The maximum is exclusive and the minimum is inclusive
    }

    function createRandomData(arrayLength: number, xMin: number, xMax: number, yMin: number, yMax: number) {
        const range: number[] = [...Array(arrayLength).keys()];
        return range.map(i => {
            return {x: getRandomInt(xMin, xMax), y: getRandomInt(yMin, yMax)}
        });
    }


    useEffect(() => {
        const initializeMap = async () => {
            const imageServer = 'http://localhost:5005';
            const tileinfo = await fetch(`${imageServer}/image/tile/info`).then(res => res.json());

            // Create the map layer
            const params = geo.util.pixelCoordinateParams(
                viewRef.current, tileinfo.sizeX, tileinfo.sizeY, tileinfo.tileWidth, tileinfo.tileHeight);
            const map = geo.map(params.map);
            params.layer.url = `${imageServer}/image/tile/{z}/{x}/{y}`;
            map.createLayer('osm', params.layer)

            // Create the annotation layer
            map.createLayer('annotation', {clickToEdit: false}).mode('polygon', undefined);


            // Create the ground truth layer
            const pointOptions = {
                style: {
                    stroke: true,
                    strokeColor: 'black',
                    strokeWidth: 1,
                    fill: true,
                    radius: 1,
                }
            }

            const groundTruthLayer = map.createLayer('feature', {features: ['point']});
            const testFeature = groundTruthLayer.createFeature('point', pointOptions);
            const data = createRandomData(10000000, 5000, 15000, 5000, 15000);
            testFeature.data(data).draw();

            return null;
        };

        initializeMap().then(r => console.log('Map initialized'));
    }, []);


    return (
        <div ref={viewRef} style={
            {
                width: '1000px',
                height: '1000px',
                position: 'relative',
                backgroundColor: 'black',
                top: 0,
                left: 0
            }
        }>
        </div>
    );
}

export default WsiView;