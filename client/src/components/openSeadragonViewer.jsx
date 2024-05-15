import React,{useEffect, useState, useRef} from 'react';
import OpenSeadragon from 'openseadragon';

class CustomTileSource extends OpenSeadragon.TileSource {
    constructor(options) {
        super(options);
        this.tilesUrl = options.tilesUrl;
    }

    getTileUrl(level, x, y) {
        return `${this.tilesUrl}/${level}/${x}/${y}`;
    }
}

const OpenSeadragonViewer = () => {
    const viewerRef = useRef(null);
    useEffect(() => {
        const viewer = OpenSeadragon({
            id: 'viewer',
            prefixUrl: 'https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/images/',
            tileSources: new CustomTileSource({
                tilesUrl: 'http://localhost:5005/image/tile',
                width: 19920,  // Adjust based on your actual image dimensions
                height: 14204, // Adjust based on your actual image dimensions
                tileSize: 240,     // Your server's tile size
                maxLevel: 5        // Adjust based on the maximum zoom level your server supports
            })
        });
        viewerRef.current = viewer;
        return () => viewerRef.current && viewerRef.current.destroy();
    }, []);
    return <div id="viewer" style={{ width: '100%', height: '500px' }} />;
};

export default OpenSeadragonViewer;