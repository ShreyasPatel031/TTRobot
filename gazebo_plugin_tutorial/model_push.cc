#include <functional>
#include <gazebo/gazebo.hh>
#include <gazebo/gazebo_client.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/transport/transport.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3.hh>
#include <ignition/math/Pose3.hh>
#include "ros/ros.h"
#include "std_msgs/String.h"

using namespace gazebo;
class ModelPush : public ModelPlugin{

    // Pointer to the model
    private: physics::ModelPtr model;

    // Pointer to the update event connection
    private: event::ConnectionPtr updateConnection;

    private: common:: Time updatePeriod,prevUpdate;

    private: transport::SubscriberPtr mySubscriber;

	public: void OnUpdate(const common::UpdateInfo &info){
		// Apply a small linear velocity to the model.

		if ( info.simTime - this->prevUpdate > this->updatePeriod){
			printf( "Time:%lf\n",info.simTime.Double());	
			this->model->SetLinkWorldPose(ignition::math::Pose3d(1.40474,0,1.52227,0,0,0),"ball");
			this->model->SetLinearVel(ignition::math::Vector3d(-2.75, 0, -0.8));
			this->model->SetAngularVel(ignition::math::Vector3d(0, 0, 0));
			prevUpdate  = info.simTime;
		}

	}

	// public: void CollisionUpdates(ConstContactsPtr &_msg){

	// }

	public: void Reset(){
		this->prevUpdate.Set(0, 0);
	}

	public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/){
		this->model = _parent;

		this->updatePeriod = common::Time(2);

		this->updateConnection = event::Events::ConnectWorldUpdateBegin(std::bind(&ModelPush::OnUpdate, this , std::placeholders::_1));

		// // if (!ros::isInitialized()){
		// int argc = 0;
		// char **argv = NULL;
		// client::setup(argc, argv);
		// ros::init(argc, argv, "force_measure");
		// // }
		// transport::NodePtr node(new transport::Node());
  		//node->Init();

		// this->mySubscriber = node->Subscribe("/gazebo/default/table_tennis_ball/ball/my_contact",CollisionUpdates);
	}	

};
GZ_REGISTER_MODEL_PLUGIN(ModelPush);
