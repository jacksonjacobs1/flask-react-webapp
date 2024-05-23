import React, { useEffect, useState, useRef } from 'react';

// @ts-ignore
import geo from "geojs";

type Annotation = {
    type: string,
    geometry: {
        type: string,
        coordinates: number[][][],
    }
    properties: {
        color: number[],
        name: string
    }
}

type Centroid = {
    type: string,
    geometry: {
        type: string,
        coordinates: number[],
        properties: {
            color: number[],
            name: string
        }
    }
}

interface FeatureCollectionResponse {
    type: string;

}

interface AnnotationCollection extends FeatureCollectionResponse {
    features: Annotation[];
}

interface CentroidCollection extends FeatureCollectionResponse {
    features: Centroid[];
}



const WsiView = () => {
    const viewRef = useRef(null);
    const [annotations, setAnnotations] = useState<AnnotationCollection | null>(null);
    const [map, setMap] = useState<geo.map | null>(null);

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

    async function getAnnotations(minx: number, miny: number, maxx: number, maxy: number) {
        fetch(`http://localhost:5005/image/annotations?minx=${minx}&miny=${miny}&maxx=${maxx}&maxy=${maxy}`)
            .then(res => res.json())
            .then((data: AnnotationCollection) => {
            setAnnotations(data);
        });
    }

    // async function getCentroids(minx: number, miny: number, maxx: number, maxy: number) {
    //     fetch(`http://localhost:5005/image/centroids?minx=${minx}&miny=${miny}&maxx=${maxx}&maxy=${maxy}&centroid`)
    //         .then(res => res.json())
    //         .then((data: FeatureCollectionResponse) => {
    //         setAnnotations(data);
    //     });
    // }


    useEffect(() => {
        const initializeMap = async () => {

            const imageServer = 'http://localhost:5005';
            const tileinfo = await fetch(`${imageServer}/image/tile/info`).then(res => res.json());

            // Create the map layer
            const params = geo.util.pixelCoordinateParams(
                viewRef.current, tileinfo.sizeX, tileinfo.sizeY, tileinfo.tileWidth, tileinfo.tileHeight);
            const map = geo.map(params.map);
            setMap(map);
            params.layer.url = `${imageServer}/image/tile/{z}/{x}/{y}`;

            map.createLayer('osm', params.layer)
            map.createLayer('annotation', {clickToEdit: false}).mode('polygon', undefined);

            map.geoOn(geo.event.mousemove, function (evt: any) {
                console.log(evt.geo.x.toFixed(6), evt.geo.y.toFixed(6));
            });


            return null;
        };

        initializeMap().then(r => console.log('Map initialized'));
    }, []);


    // Create a feature layer when the annotations are loaded
    useEffect(() => {
        const initializeFeatureLayer = async () => {
            if (!annotations) {
                await getAnnotations(30000, 30000, 40000, 40000);
            } else {
                console.log(annotations)
            }

            if (map && annotations) {
                // const pointOptions = {
                //     style: {
                //         stroke: true,
                //         strokeColor: 'black',
                //         strokeWidth: 1,
                //         fill: true,
                //         radius: 1,
                //     }
                // }

                const layer = map.createLayer('feature', {features: ['polygon', 'point']})
                var polygons = layer.createFeature('polygon', {selectionAPI: true});


                polygons
                    .data(annotations.features.map(f => {
                        return {
                            type: f.geometry.type,
                            coordinates: f.geometry.coordinates,
                            properties: f.properties
                        }
                    }))
                    .style('fill', true)
                    .style('fillOpacity', 0.1)
                    .style('stroke', false)
                    .style('fillColor', (d: number[], idx: number, poly: any, polyidx: number) => {
                        return `rgb(${poly.properties.color[0]}, ${poly.properties.color[1]}, ${poly.properties.color[2]})`
                    })
                    .polygon(function (d: any) {

                        return {
                            outer: d.coordinates[0]
                        };
                    })
                    .position((d: number[]) => {
                        return {x: d[0], y: d[1]}
                    })
                    .geoOn(geo.event.feature.mouseclick, function (evt: any) {
                        console.log(evt.data.properties.name);

                    });


                    polygons.draw();

            }
        }

        initializeFeatureLayer().then(r => console.log('Feature layer initialized'));
        // testFeature.data(data).draw();
    }, [annotations, map]);


    return (
        <div ref={viewRef} style={
            {
                width: '95vw',
                height: '95vh',
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