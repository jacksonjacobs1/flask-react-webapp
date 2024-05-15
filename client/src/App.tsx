import React from 'react';
// import './App.css';
import WsiView from "./components/wsiView";
import WsiViewHook from "./components/wsiViewHook";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p>Test WSI viewer for quickannotator</p>
      </header>
        {/*<OpenSeadragonViewer />*/}
        {/*<WsiView />*/}
        <WsiViewHook />

    </div>
  );
}

export default App;
