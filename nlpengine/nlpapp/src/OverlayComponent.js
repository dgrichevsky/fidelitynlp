import React from 'react';
import {  Modal } from 'reactstrap';
import SpinnerComponent from './SpinnerComponent';
import './style.css';

class OverlayComponent extends React.Component {
	constructor(props) {
		super(props);
		this.state = {isLoading: false};


	}
	componentWillReceiveProps(props) {
		this.setState({ isLoading: props.isLoading });
	}

	render() {
		return (
			<Modal contentClassName="overlay"
				isOpen={this.state.isLoading} scrollable={false} centered={true}>

				<SpinnerComponent className="loading"> </SpinnerComponent>
			</Modal>
		);
	}
}

export default OverlayComponent;