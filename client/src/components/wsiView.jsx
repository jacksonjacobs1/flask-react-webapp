import React, { Component } from 'react';
import geo from 'geojs';

class WsiView extends Component {
    constructor(props) {
        super(props);
        this.viewRef = React.createRef();
        this.map = null; // Reference to the GeoJS map
        this.state = {
            clickPosition: null,
            zoomLevel: null
        };
    }

    componentDidMount() {
        const imageServer = 'http://localhost:5005';
        const initializeMap = async () => {
            const tileinfo = await fetch(`${imageServer}/image/tile/info`).then(res => res.json());
            const params = geo.util.pixelCoordinateParams(
                this.viewRef.current, tileinfo.sizeX, tileinfo.sizeY, tileinfo.tileWidth, tileinfo.tileHeight
            );
            this.map = geo.map(params.map);
            params.layer.url = `${imageServer}/image/tile/{z}/{x}/{y}`;
            this.layer = this.map.createLayer('osm', params.layer);
        };

        initializeMap();
    }

    // componentDidUpdate(prevProps, prevState) {
    //     if (prevState.zoomLevel !== this.state.zoomLevel) {
    //         // Assuming that a change in zoom level requires reconfiguration of the layer
    //         this.updateLayer();
    //     }
    // }
    //
    // updateLayer() {
    //     // Example logic: adjust layer visibility or redraw based on zoom level
    //     if (this.map) {
    //         // You might reconfigure the layer here, or simply force a redraw
    //         this.layer.draw();
    //     }
    //     console.log('Layer updated');
    // }

    render() {
        return (
            <div ref={this.viewRef} style={{
                width: '1000px',
                height: '1000px',
                position: 'relative',
                top: 0,
                left: 0,
            }}>
                <p>Last click at: X {this.state.clickPosition?.x}, Y {this.state.clickPosition?.y}</p>
                <p>Current Zoom Level: {this.state.zoomLevel}</p>
            </div>
        );
    }
}

export default WsiView;