import React from 'react';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap';
import JsonTable from 'ts-react-json-table';
import WordCloud from 'react-d3-cloud';

class ModalComponent extends React.Component {
	constructor(props) {
		super(props);
		this.state = {modal: false};

		this.saveModel = this.saveModel.bind(this);
	}
	componentWillReceiveProps(props) {
		this.setState({ modal: props.modal });
	}
	saveModel() {
		this.setState({modal : false});
	}
	render() {

		return (
			<div>
				{this.props.apply && <div>
					<Modal isOpen={this.state.modal} toggle={this.props.action} scrollable={true} className={this.props.className}>
						<ModalHeader toggle={this.props.action}>Term Frequency-Inverse Document Frequency</ModalHeader>
						<ModalBody>
							{this.props.currentModel}
						</ModalBody>
						<ModalFooter>
							<Button color="primary" onClick={this.props.action}>OK</Button>{' '}
							</ModalFooter>
						</Modal>

					</div>}
					{this.props.other && <div>
						<Modal isOpen={this.state.modal} toggle={this.props.action} scrollable={true} className={this.props.className}>
							<ModalHeader toggle={this.props.action}>Output of Model</ModalHeader>
							<ModalBody>
								<JsonTable className="table" rows = {this.props.currentModel} / >
									{this.props.wordCloud.map((topic, count) =>
										<div className="topics" key={count}> Topic {count}
											<WordCloud data={topic} height={250} width={400} /> </div> )}
							</ModalBody>
								<ModalFooter>
									<Button color="primary" onClick={this.props.action}>Save my Model</Button>{' '}
									</ModalFooter>
								</Modal>
										</div>

									}
								</div>
							);
						}
					}
					export default ModalComponent;