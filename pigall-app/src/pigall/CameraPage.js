import React, { Component }  from 'react';
import { Page, BottomToolbar, Segment, ToolbarButton } from 'react-onsenui';

/**
 * Main Application Page for PigallApp
 */
class CameraPage extends Component {

    /**
     * Default Constructor
     * @param {*} props     Inbound Properties
     */
    constructor(props) {
        super(props);
        this.state = {
            videoFeedURL: '/raw_video_feed',
            currentImage: 0
        }
    }

    componentDidUpdate() {
        var headers = new Headers({'X-Mashape-Key': 'API_KEY'});
        var options = {
            method: 'GET',
            headers: headers,
            mode: 'cors',
            cache: 'default'
        };
        var request = new Request(this.state.videoFeedURL);

        fetch(request, options).then(res => res.json()).then(data => {
            var base64Flag = 'data:image/jpeg;base64,'
            var imageStr = data.ImageBytes
            this.setState({ currentImage: base64Flag + imageStr })
        });
    }

    /**
     * Event Handler when the take photo button is clicked
     * @param {*} _event    Event of this handler
     */
    takePhoto(_event) {
        document.getElementById("imgScanned").click()
    }

    /**
     * React JS Render function
     */
    render() {
        return(
<Page>
    <img src={ this.state.currentImage } />
    <BottomToolbar modifier="material">
        <Segment style={{width: '100%'}} modifier="material">
            <ToolbarButton
                onClick={
                    (_event) => {this.takePhoto(_event)}
                }
            >Take Photo</ToolbarButton>
        </Segment>
    </BottomToolbar>
</Page>
        );
    }
}

// Default exported component
export default CameraPage;
