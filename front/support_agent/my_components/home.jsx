import { Blockquote, Box, Button, List, ScrollArea, Title, Text } from '@mantine/core';
import { IconHome, IconMailbox } from '@tabler/icons-react';

function Home(props) {
  const icon = <IconHome />;

  return (
    // 1. The outer wrapper sets the maximum height.
    // This creates the boundary for our component.
    <Box className='limited-height-flex custom-font-body'>

      {/* 2. The inner container fills the wrapper and manages the layout.
          It now has a defined height to distribute to its children. */}
      <Blockquote color="blue" icon={icon} mt="xl" className='fill-flex-column'>
        {/* 3. The scrollable area grows to fill the remaining space.
            Since its parent (Blockquote) has a defined height, scrolling now works. */}
        <ScrollArea style={{ flexGrow: 1 }}>
            <Title size="lg" className='justify-left custom-font-body' order={1}>Welcome to the Support Hub</Title>
            <Text className='justify-left'>
                - Your central dashboard for managing all customer interactions with ease and efficiency.
                 From tracking orders to handling payments, this hub empowers you to deliver top-tier support.
                  Let’s get started!
            </Text>

            <List w='100%'>
            <List.Item className='justify-left' pt={10}><Context section='inbox'/></List.Item>
            <List.Item className='justify-left' pt={10}><Context section='sops'/></List.Item>
            <List.Item className='justify-left' pt={10}><Context section='orders'/></List.Item>
            <List.Item className='justify-left' pt={10}><Context section='payments'/></List.Item>
            <List.Item className='justify-left' pt={10}><Context section='shipments'/></List.Item>
            <List.Item className='justify-left' pt={10}><Context section='invoices'/></List.Item>

            </List>
        </ScrollArea>

        {/* 4. The button stays at the bottom. */}
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <Button variant="light" color="lime" size="xs" onClick={props.clickHandler}>
            Let's Start
          </Button>
        </div>
        
      </Blockquote>
    </Box>
  );
}


function Context(props){
    if (props.section == 'inbox'){
        return(
        <>
            <Text td="underline" fs="italic"> INBOX:</Text>
            <Text>Access all incoming customer support requests. View, respond to, 
                and categorize cases to ensure every customer receives timely and accurate help. 
                Prioritize urgent issues and assign tasks to relevant team members.</Text>
        </>
        );
    }
    else if (props.section == 'sops'){
        return(
        <>
            <Text td="underline" fs="italic">STANDARD OPERATING PROCEDURES:</Text>
            <Text>Browse and follow your team’s Standard Operating Procedures.
                These documents outline approved workflows, best practices,
                 and escalation paths to help you maintain consistency and quality in customer support.</Text>
        </>
        );
    }
    else if (props.section == 'orders'){
        return(
        <>
            <Text td="underline" fs="italic">ORDER LOOKUP AND STATUS TRACKING:</Text>
            <Text>Quickly retrieve customer order details. Use this tool to verify product purchases,
                 check fulfillment status, view order history, 
                 or assist customers with tracking or modifying their orders.</Text>
        </>
        );
    }
    else if (props.section == 'payments'){
        return(
        <>
            <Text td="underline" fs="italic">PAYMENT AND BILLING QUERIES:</Text>
            <Text>Handle all payment-related inquiries. This section allows you to view transaction history, 
                resolve billing discrepancies, process refunds, and answer questions about charges or failed payments.</Text>
        </>
        );
    }
    else if (props.section == 'shipments'){
        return(
        <>
            <Text td="underline" fs="italic">SHIPPING AND DELIVERY TRACKING:</Text>
            <Text>Track and manage shipping logistics. View delivery status, carrier information,
                 and estimated arrival times. Support customers with delayed or lost packages by 
                 initiating investigations or re-shipments.</Text>
        </>
        );
    }
    else if (props.section == 'invoices'){
        return(
        <>
            <Text td="underline" fs="italic">INVOICE MANAGEMENT:</Text>
            <Text>Generate, send, and track customer invoices. Resolve invoice disputes, 
                verify payment status, and make adjustments when necessary. 
                Keep financial documentation clear and up to date.</Text>
        </>
        );
    }
    
}

export default Home;