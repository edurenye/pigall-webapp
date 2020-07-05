import React, { Component }  from 'react';
import { Page, Toolbar } from 'react-onsenui';

// Application Page components
import CameraPage from './CameraPage.js';

// Constant values for Instruction Messages
const TOOLBAR_MESSAGE = 'Pigall';

/**
 * Main Application Page for PigallApp
 */
class PigallApp extends Component {

    /**
     * Default Constructor
     * @param {*} props     Inbound Properties
     */
    constructor(props) {
        super(props);
        this.state = {
            toolbar_msg: TOOLBAR_MESSAGE
        }
    }

    /**
     * React JS Render function
     */
    render() {
        return(
<Page id="MainPage" renderToolbar={() =>
    <Toolbar>
        <div className="center">
            { this.state.toolbar_msg }
        </div>
    </Toolbar>
}>
    <CameraPage></CameraPage>
</Page>
        );
    }
}

// Default exported component
export default PigallApp;
